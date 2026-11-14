# 道可道·坛经 1.2.0（安卓离线包）

- 包名 `com.daokedao.tanjing`，versionCode 12000，versionName 1.2.0
- 大小 1,512,484 字节
- **零权限**：`aapt2 dump badging` 权限计 0；全书与字体均在 assets 内，断网可用
- 字体：`TanjingSerif` 本地 woff 子集（1,615 用字，Regular 622,944 B／Bold 641,684 B）
- 签名证书 SHA-256 `2B:DC:24:68:38:52:14:BD:D3:A7:D9:35:0E:59:06:95:4F:62:6E:32:B9:0D:3F:A5:E2:B2:19:74:A8:5A:6C:EA`（与道德经、易传、心经、庄子、金刚经同一把）
- 来源：`apk/build.sh` 六步链（aapt2 → d8 → zipalign → apksigner），资产由 `apk/prepare-assets.py` 生成

校验：`sha256sum -c SHA256SUMS`
