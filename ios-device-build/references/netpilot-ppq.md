# NetPilot and Apple profile validation

Use this reference only when the target iPhone runs the user's NetPilot app (`dev.hanjialu.netpilot`) and device logs prove that `ppq.apple.com` validation is failing.

## Why ordinary split mode can fail

NetPilot's iOS Packet Tunnel sends DNS through a fake-IP pipeline. A domain may therefore enter the tunnel even when the final rule is `DIRECT`. In the observed failure, `https://ppq.apple.com/v2/authorization` ended with `NSURLErrorDomain -1200` and SecureTransport `errSSLClosedNoNotify (-9816)`. Switching to a working proxy route allowed iOS to validate the profile immediately.

Do not rebuild the app or strip entitlements when the log already says `Profile Needs Network Validation`.

## Reversible recovery

Read and preserve the current NetPilot mode first. Prefer a route that keeps the device online. The supported deep links are:

```text
netpilot://mode/off
netpilot://mode/split
netpilot://mode/global
```

For this observed route, temporarily select global mode:

```bash
IOS_DEVELOPER_DIR=/Applications/Xcode-beta.app/Contents/Developer
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl device process launch \
  --device <device> \
  --payload-url 'netpilot://mode/global' \
  --no-activate \
  dev.hanjialu.netpilot
```

Retry the target app launch once. When launch succeeds, restore the original mode, normally split:

```bash
DEVELOPER_DIR="$IOS_DEVELOPER_DIR" xcrun devicectl device process launch \
  --device <device> \
  --payload-url 'netpilot://mode/split' \
  --no-activate \
  dev.hanjialu.netpilot
```

Do not assume the deep link completed. Verify the restored state through NetPilot's UI or a read-only diagnostic snapshot. If global still fails, temporarily turning NetPilot off is the next bounded diagnostic; restore the original mode immediately afterward.

## Long-term product fix

A durable NetPilot fix belongs in the NetPilot project, not in the app being installed. Test whether excluding `+.ppq.apple.com` from fake-IP or providing an explicit trusted route restores profile validation without weakening other traffic policies. That change needs its own regression coverage and user authorization.
