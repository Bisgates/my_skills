---
name: ios-device-build
description: Build, sign, install, launch, and verify an iOS app on a physical iPhone or iPad with Xcode and devicectl. Use when the user asks to build for a real iOS device, install an app on an iPhone, test through iPhone Mirroring, diagnose CoreDeviceError 10002 or developer-profile trust, or says “真机 build / 装机 / 安装到手机”. Do not use Simulator or generic iphoneos builds as physical-device acceptance.
---

# iOS physical-device build

Physical-device acceptance is a causal chain: resolve the intended device, build specifically for that destination, verify the signed product, install that exact product, then prove launch and the requested interaction on the device. A generic `iphoneos` build proves compilation and signing only; it does not prove that the installed device can validate or launch the profile.

## Quick start

Use the bundled helper for the repeatable build/sign/install path:

```bash
~/.codex/skills/ios-device-build/scripts/build_for_device.sh \
  --project ios/App.xcodeproj \
  --scheme App \
  --device <CoreDevice-ID-or-UDID> \
  --install
```

The helper builds for `-destination id=<device>`, verifies the app with `codesign --deep --strict`, and installs only when `--install` is explicit. Add `--launch` only when the user also authorized launching the app.

## Workflow

### 1. Establish the contract before changing device state

- Inspect repository instructions and existing build/install scripts first. Reuse the project's destination, scheme, configuration, entitlements, and provisioning conventions.
- Preserve unrelated dirty work and user data. A physical install overwrites the app bundle but may retain its container; do not uninstall unless the user explicitly wants a clean install.
- Treat build, install, launch, profile trust, and UI interaction as distinct permissions. Building is local; installing mutates the device; launching changes its foreground state; trusting a developer profile is a persistent security decision.
- If tests must not steal Mac focus, build and install from the terminal. Launch only after authorization, and use iPhone Mirroring for interaction when requested.

### 2. Resolve Xcode and the real device

The active `xcode-select` path may be Command Line Tools. Resolve an actual Xcode developer directory and keep it explicit for every Xcode command:

```bash
IOS_DEVELOPER_DIR=/Applications/Xcode-beta.app/Contents/Developer
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcodebuild -version
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl list devices
```

Record both identifiers:

- CoreDevice ID: useful for `xcodebuild -destination id=...` and accepted by `devicectl`.
- Hardware UDID: required by `idevicesyslog` and some libimobiledevice tools.

Confirm the target is paired, connected, booted, has Developer Mode enabled, and is not passcode-blocked:

```bash
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl device info details --device <device>
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl device info lockState --device <device>
```

Do not substitute a Simulator merely because the physical device is temporarily unavailable. Report that boundary explicitly.

### 3. Build for the device destination

The destination-specific pattern is:

```bash
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcodebuild \
  -project ios/App.xcodeproj \
  -scheme App \
  -configuration Debug \
  -destination 'id=<CoreDevice-ID-or-UDID>' \
  -derivedDataPath /tmp/app-device-build \
  -allowProvisioningUpdates \
  build
```

Use a workspace when the repository does. Keep DerivedData outside the repository. A destination-specific build lets Xcode select the device platform, provisioning profile, registered-device membership, and restricted entitlements together.

Run focused tests and `git diff --check` as separate gates. Do not erase unrelated warnings or dirty files merely to make the gate visually clean; scope and report them.

### 4. Verify the exact product before installation

Resolve `TARGET_BUILD_DIR` and `WRAPPER_NAME` with `xcodebuild -showBuildSettings` using the same destination and DerivedData, then verify:

```bash
codesign --verify --deep --strict /path/to/App.app
codesign -dv --verbose=4 /path/to/App.app
codesign -d --entitlements :- /path/to/App.app
security cms -D -i /path/to/App.app/embedded.mobileprovision
```

Check the whole chain:

- `CFBundleIdentifier` matches the intended app.
- `application-identifier` and Team ID agree between signature and profile.
- The profile is unexpired and includes the physical device UDID.
- Every restricted app entitlement is authorized by the embedded profile.
- The app being installed is this destination-specific product, not an older generic build.

### 5. Install, then prove launch separately

Install the exact app without launching it automatically:

```bash
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl device install app \
  --device <device> /path/to/App.app
```

If launch is authorized, run it as an independent gate:

```bash
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl device process launch \
  --device <device> --terminate-existing <bundle.identifier>
```

An install success does not imply a launch success. Preserve the full `devicectl` error chain when launch fails.

### 6. Diagnose first-launch trust and network validation

For `CoreDeviceError 10002`, do not immediately rebuild or strip entitlements. Separate these branches:

| Evidence | Meaning | Next action |
|---|---|---|
| `codesign --verify` fails | Product corruption/signing failure | Rebuild and inspect signing inputs |
| App entitlements exceed profile entitlements | Provisioning mismatch | Fix the App ID/profile; do not delete the feature entitlement |
| `Profile Needs Network Validation`, `Requires Network Validation`, `0xe8008026` | Device must validate the development profile online | Check the device route to `https://ppq.apple.com` |
| User-facing untrusted developer prompt | Persistent device trust is missing | Ask before changing Settings trust state |
| Device locked / Developer Mode disabled | Runtime policy blocks launch | Have the user unlock or enable Developer Mode |

Capture a focused device log around one launch attempt. `idevicesyslog` needs the hardware UDID:

```bash
idevicesyslog -n -u <hardware-UDID> --no-colors \
  -p 'SpringBoard|amfid|installd|trustd|securityd' \
  -o /tmp/ios-device-launch.log
```

If the log names `ppq.apple.com`, capture that path directly. `NSURLErrorDomain -1200` with SecureTransport `-9816` means the TLS peer closed without a close notification; investigate the device's VPN, proxy, DNS/fake-IP, firewall, or route instead of changing app signing.

Apple requires online access to validate manually installed developer certificates. When a firewall is involved, allow `https://ppq.apple.com`.

For the user's NetPilot-specific, reversible PPQ recovery, read [references/netpilot-ppq.md](references/netpilot-ppq.md). Do not apply it on devices without NetPilot.

### 7. Verify through iPhone Mirroring without writing user data

When the user asks for iPhone Mirroring:

1. Lock the physical iPhone; Mirroring refuses to connect while the phone is in use.
2. If remote sleep is appropriate and authorized, `idevicediagnostics -n -u <hardware-UDID> sleep` can place it into sleep mode.
3. Connect iPhone Mirroring and inspect the current installed build.
4. Test navigation, expansion, filtering, scrolling, and cancellation paths first. Avoid creating real records, sending messages, granting permissions, or syncing external state unless the user asked for those mutations.
5. Capture the important screens and compare them with the supplied design at the same state and viewport when visual fidelity is part of acceptance.

iPhone Mirroring intentionally uses the Mac keyboard for text entry, so the iOS software keyboard need not appear. A visible caret plus successful Mac typing proves focus; absence of the on-screen keyboard alone is not an app defect.

If the phone is touched physically during a mirroring session, re-read the current UI state before sending another action. Never click a profile-trust, privacy, VPN, or permission confirmation merely because it blocks the test; obtain explicit confirmation at that boundary.

## Completion evidence

Report physical-device acceptance only when the requested chain is observed:

- destination-specific Xcode build succeeded;
- exact app path and bundle identifier resolved;
- strict code-sign verification succeeded;
- install succeeded on the named physical device;
- launch succeeded, or the remaining device-side trust boundary is stated precisely;
- requested device UI interactions were exercised without unintended writes;
- any temporary network mode or device setting was restored and verified.

Keep Simulator results separate. Do not claim end-to-end cloud or local-network sync unless the real exchange was observed.

## Gotchas

- `-sdk iphoneos -destination 'generic/platform=iOS'` is a compile/sign preflight, not the final physical-device build.
- `devicectl` accepts several device identifiers; `idevicesyslog` generally requires the hardware UDID.
- Reinstalling does not repair a profile that still needs online validation.
- Removing Family Controls, Network Extension, CloudKit, or other restricted entitlements just to make launch succeed breaks the product contract.
- A VPN route can allow ordinary browsing while still breaking `ppq.apple.com`; validate the exact endpoint.
- Restore temporary VPN/proxy mode changes and verify the restored state.

## See also

- [references/netpilot-ppq.md](references/netpilot-ppq.md) — NetPilot-specific PPQ validation and restoration.
- [EVALS.md](EVALS.md) — realistic trigger and outcome checks.
