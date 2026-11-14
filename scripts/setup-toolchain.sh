#!/usr/bin/env bash
# 准备 Android 构建工具链（一次性，之后可反复用）。
#
# 装到常驻目录：$TOOLCHAIN（默认 ~/.daokedao-vault/toolchain）
#   jdk-11*/        Temurin JDK 11（含 javac / keytool）
#   android-14/     build-tools 34（aapt2 / d8 / zipalign / apksigner）
#   android-35/     platform 35（android.jar）
#
# 换机器或容器重建后，先跑一次本脚本，再跑各仓 apk/build.sh。
# 用法：bash scripts/setup-toolchain.sh
set -euo pipefail

TC=${TOOLCHAIN:-$HOME/.daokedao-vault/toolchain}
mkdir -p "$TC"
cd "$TC"

needs_jdk=1; needs_bt=1; needs_pf=1
ls -d jdk-11* >/dev/null 2>&1 && [ -x "$(ls -d jdk-11*/ | head -1)bin/javac" ] && needs_jdk=0 || true
[ -x android-14/aapt2 ] && needs_bt=0 || true
[ -f android-35/android.jar ] && needs_pf=0 || true

if [ $needs_bt -eq 1 ]; then
  echo "== build-tools 34 =="
  curl -sL -o bt.zip https://dl.google.com/android/repository/build-tools_r34-linux.zip
  unzip -q -o bt.zip && rm -f bt.zip
fi
if [ $needs_pf -eq 1 ]; then
  echo "== platform 35 =="
  curl -sL -o pf.zip https://dl.google.com/android/repository/platform-35_r02.zip
  unzip -q -o pf.zip && rm -f pf.zip
fi
if [ $needs_jdk -eq 1 ]; then
  echo "== JDK 11 =="
  curl -sL -o jdk.tar.gz "https://api.adoptium.net/v3/binary/latest/11/ga/linux/x64/jdk/hotspot/normal/eclipse"
  tar xzf jdk.tar.gz && rm -f jdk.tar.gz
fi

echo "---"
ls -d "$TC"/jdk-11*/ "$TC"/android-14 "$TC"/android-35
"$(ls -d "$TC"/jdk-11*/ | head -1)bin/javac" -version
"$TC/android-14/aapt2" version 2>&1 | head -1
echo "✓ 工具链就绪：$TC"
