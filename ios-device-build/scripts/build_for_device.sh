#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  build_for_device.sh (--project PATH | --workspace PATH) --scheme NAME --device ID [options]

Required:
  --project PATH          Xcode project path
  --workspace PATH        Xcode workspace path (mutually exclusive with --project)
  --scheme NAME           Xcode scheme
  --device ID             CoreDevice ID or device UDID

Options:
  --configuration NAME    Build configuration (default: Debug)
  --developer-dir PATH    Xcode Developer directory
  --derived-data PATH     DerivedData directory (default: a new /tmp directory)
  --install               Install the verified app on the device
  --launch                Launch after installation; implies --install
  --no-terminate          Do not terminate an existing app process before launch
  -h, --help              Show this help

The script always uses a device-specific Xcode destination and verifies the
result with codesign --deep --strict. It never uninstalls the existing app.
EOF
}

ios_project=""
ios_workspace=""
ios_scheme=""
ios_device=""
ios_configuration="Debug"
ios_developer_dir=""
ios_derived_data=""
ios_install=0
ios_launch=0
ios_terminate=1

while (($#)); do
  case "$1" in
    --project) ios_project=${2:?missing value for --project}; shift 2 ;;
    --workspace) ios_workspace=${2:?missing value for --workspace}; shift 2 ;;
    --scheme) ios_scheme=${2:?missing value for --scheme}; shift 2 ;;
    --device) ios_device=${2:?missing value for --device}; shift 2 ;;
    --configuration) ios_configuration=${2:?missing value for --configuration}; shift 2 ;;
    --developer-dir) ios_developer_dir=${2:?missing value for --developer-dir}; shift 2 ;;
    --derived-data) ios_derived_data=${2:?missing value for --derived-data}; shift 2 ;;
    --install) ios_install=1; shift ;;
    --launch) ios_launch=1; ios_install=1; shift ;;
    --no-terminate) ios_terminate=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -n "$ios_project" && -n "$ios_workspace" ]]; then
  printf 'Choose either --project or --workspace, not both.\n' >&2
  exit 2
fi
if [[ -z "$ios_project" && -z "$ios_workspace" ]]; then
  printf 'One of --project or --workspace is required.\n' >&2
  exit 2
fi
if [[ -z "$ios_scheme" || -z "$ios_device" ]]; then
  printf -- '--scheme and --device are required.\n' >&2
  exit 2
fi

if [[ -z "$ios_developer_dir" ]]; then
  if [[ -x /Applications/Xcode-beta.app/Contents/Developer/usr/bin/xcodebuild ]]; then
    ios_developer_dir=/Applications/Xcode-beta.app/Contents/Developer
  else
    ios_developer_dir=$(xcode-select -p)
  fi
fi
if [[ ! -x "$ios_developer_dir/usr/bin/xcodebuild" ]]; then
  printf 'No xcodebuild at %s/usr/bin/xcodebuild\n' "$ios_developer_dir" >&2
  exit 2
fi

if [[ -z "$ios_derived_data" ]]; then
  ios_derived_data=$(mktemp -d /tmp/ios-device-build.XXXXXX)
fi
mkdir -p "$ios_derived_data"

if [[ -n "$ios_project" ]]; then
  ios_locator=(-project "$ios_project")
else
  ios_locator=(-workspace "$ios_workspace")
fi

ios_common=(
  "${ios_locator[@]}"
  -scheme "$ios_scheme"
  -configuration "$ios_configuration"
  -destination "id=$ios_device"
  -derivedDataPath "$ios_derived_data"
  -allowProvisioningUpdates
)

printf 'Developer dir: %s\n' "$ios_developer_dir"
printf 'Device:        %s\n' "$ios_device"
printf 'DerivedData:   %s\n' "$ios_derived_data"

DEVELOPER_DIR="$ios_developer_dir" xcrun devicectl device info details --device "$ios_device" >/dev/null
DEVELOPER_DIR="$ios_developer_dir" xcodebuild "${ios_common[@]}" build

ios_settings=$(DEVELOPER_DIR="$ios_developer_dir" xcodebuild "${ios_common[@]}" -showBuildSettings)
ios_target_dir=$(awk -F ' = ' '/^[[:space:]]*TARGET_BUILD_DIR = / { print $2; exit }' <<<"$ios_settings")
ios_wrapper_name=$(awk -F ' = ' '/^[[:space:]]*WRAPPER_NAME = / { print $2; exit }' <<<"$ios_settings")

if [[ -z "$ios_target_dir" || -z "$ios_wrapper_name" ]]; then
  printf 'Could not resolve TARGET_BUILD_DIR or WRAPPER_NAME.\n' >&2
  exit 1
fi

ios_app_path="$ios_target_dir/$ios_wrapper_name"
if [[ ! -d "$ios_app_path" ]]; then
  printf 'Built app not found at %s\n' "$ios_app_path" >&2
  exit 1
fi

codesign --verify --deep --strict "$ios_app_path"
ios_bundle_id=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$ios_app_path/Info.plist")

printf 'App:           %s\n' "$ios_app_path"
printf 'Bundle ID:     %s\n' "$ios_bundle_id"
printf 'Code signing:  verified (deep, strict)\n'

if ((ios_install)); then
  DEVELOPER_DIR="$ios_developer_dir" xcrun devicectl device install app \
    --device "$ios_device" "$ios_app_path"
fi

if ((ios_launch)); then
  ios_launch_args=(device process launch --device "$ios_device")
  if ((ios_terminate)); then
    ios_launch_args+=(--terminate-existing)
  fi
  ios_launch_args+=("$ios_bundle_id")
  DEVELOPER_DIR="$ios_developer_dir" xcrun devicectl "${ios_launch_args[@]}"
fi
