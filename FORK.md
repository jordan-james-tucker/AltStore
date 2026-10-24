# Independent AltStore Classic build

This fork starts from the official `altstoreio/AltStore` Classic branch at
`bbc10d6964185b75a46c6ddd7476ac08df095308` (Classic 2.3.1; Oct 21, 2026).
Its parent `44ce4a571d1d662da03329b060752279774517f7` sets the app version;
the final upstream commit only updates the desktop AltServer version.
The official background processing, pairing delivery, migrations, source matching,
reset behavior and HTTP error explanations are retained.

## Changes

1. Mac ADI providers remain available alongside the current official directory.
   A specifically selected provider is honored. Automatic selection tries the
   bundled Mac providers before the remaining directory entries and can use the
   cached list if the directory is unavailable.
2. Use the provider's advertised User-Agent throughout authentication. Bind the
   cached provisioning blob to its origin, client info and User-Agent. Fetch a
   fresh OTP after verification; pin the provider and device identity for one
   authentication attempt, including Apple's resynchronization challenge.
3. Preserve the existing desktop wire protocol. Desktop OTP refresh is supported;
   a desktop resynchronization challenge fails explicitly because that protocol
   cannot carry it. The Mac-provider path uses Remote AltServer on the phone.
4. If the cached device UDID is absent/empty, use the UDID already embedded in
   Classic's signed Info.plist. Error 1006 retains its code and now identifies
   the source file/line where it originated. No device identifiers are logged.
   This is a candidate fix: the cause of intermittent overnight failures has
   not been proven, and compiling it does not establish that overnight refresh works.

The compatibility work is adapted from `liuzhe1117/AltStore` commit
`31972b5eb79a9df5badf25a0c073a033c7770db4` and its AltSign dependency
`020ddb5691ffb9b75dfdd92b83a6809bbfdd1d5b`, reviewed and independently built
previously. Existing upstream and dependency licenses continue to apply.
Only the needed authentication changes are ported; the older fork's desktop
protocol, extra settings UI and older background scheduler are not imported.

## Reproduce a build

Initialize the pinned submodules recursively, then run `python3 Scripts/prepare-build.py`.
This applies `Patches/AltSign-authentication-identity.patch` to the official pinned
AltSign revision `e639bdfbea185d5c229b11f62e25c5d78649d5c4`. The accompanying JSON
verifies the revision, patch and before/after source hashes. It is deliberately
tracked as a plain-text dependency patch rather than an opaque replacement binary.

The manual **Build official Classic fork** workflow builds the exact selected
repository commit on a standard GitHub macOS runner. It requires a public repo,
uses read-only repository permissions, locked Swift packages, the committed Pods,
and no Apple account or signing credentials. It emits an unsigned IPA and build
evidence for one day. There are no push, pull-request or scheduled build triggers.
The artifact records its source commit, dependency pins, patch hashes, environment,
run identity and IPA SHA-256. Local signing/installation are separate steps.

Xcode 27 requires realigning the existing universal libcurl archive container.
`Scripts/repack_curl_container.py` checks its original SHA-256 and verifies that
every architecture's archive payload is byte-for-byte identical after alignment.
It changes only the outer container offsets/alignment and padding. The workflow
sets the deployment target to iOS 17.4 for compatibility with the current SDK.
The initial custom build number is 75, app version 2.3.1.

## Verification still required on a device

Install over the existing app using the same signing identities and app groups;
do not uninstall first. Verify existing app/source entries and data, then refresh
manually using the working Mac ADI provider. Next test a scheduled locked-phone
refresh without USB, and finally the usual overnight automation. A previous
scheduled locked-phone test with USB succeeded, so it did not reproduce the 4 a.m.
failure. Retain a signed copy of the previously working build for rollback;
rolling back app code does not necessarily reverse database/settings migrations.
