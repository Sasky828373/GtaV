# GTA V Android Native – Gold Baseline

This repository is built around the graphics-correct Gold APK.

## Immutable baseline
- File: `GTAV-GOLD.apk`
- SHA-256: `c7db44f0decdbe07ca2302ac4a4c75728eb085530f4ea1b2da9639b35e05fd93`
- Gold renderer SHA-256: `0560f9209bf12117320d884d63a48b23b1abe4c963cc74ff4e6f6a48431eaaac`
- Gold libgtav.so SHA-256: `2e7a8b43b47429af7c49645ca23fc7c7c741c71087fa6ea4178b0fac718cf02a`

Rule: never replace the Gold APK in-place. Every experimental build starts from it.

The workflow verifies the exact Gold APK, extracts it, optionally injects a replacement `patch/libgtav_native_renderer.so`, repacks without recompressing native libraries, and publishes an unsigned test APK as an Actions artifact.
