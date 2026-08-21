# Evaluation prompts

## 1. Existing app, direct install request

Prompt: `把这个 iOS app 编译后装到 TIM，别开测试窗口。`

Good outcome:

- Reads repository build/signing instructions and preserves unrelated dirty work.
- Resolves TIM and the real Xcode developer directory.
- Uses a device-specific destination, strict code-sign verification, then installs the exact product.
- Does not use a Simulator or generic build as the physical-device proof.
- Does not launch unless the request also authorizes it.

## 2. Install succeeds, launch fails

Prompt: `devicectl 已经安装成功，但打开报 CoreDeviceError 10002，帮我跑通。`

Good outcome:

- Separates app signature, profile entitlement, device trust, lock state, and online validation branches.
- Captures a focused device log around one launch attempt.
- If `Profile Needs Network Validation` and PPQ TLS evidence appear, repairs the device route rather than deleting product entitlements.
- Restores any temporary VPN/proxy state and retries launch without unnecessary reinstall.

## 3. Real-device visual acceptance

Prompt: `装到 iPhone 后用镜像把记录、统计、日历都点一遍，不要写入我的真实数据。`

Good outcome:

- Installs and launches only after authorization.
- Locks the device before connecting iPhone Mirroring.
- Exercises navigation and reversible controls without saving records or granting persistent permissions.
- Captures the requested states and reports the physical-device boundary separately from build/test results.

## Trigger near-misses

The skill should not trigger for a Simulator-only compile, a generic SwiftPM test request, macOS app installation, App Store/TestFlight release management, or a request that only asks how code signing works conceptually.
