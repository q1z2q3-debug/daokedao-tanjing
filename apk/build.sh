#!/usr/bin/env bash
# 把《润泽说 道可道之坛经》v1.2.0 阅读页打成离线 APK。
#
# 产物：apk/dist/道可道-坛经-1.2.0.apk
#
# 工具链（不在仓库内，常驻 ~/.daokedao-vault/toolchain，可用 bash scripts/setup-toolchain.sh 重建）：
#   $TOOLCHAIN/jdk-11*/bin/{javac,keytool}
#   $TOOLCHAIN/android-14/{aapt2,d8,zipalign,apksigner}
#   $TOOLCHAIN/android-35/android.jar
# 签名密钥同样常驻：~/.daokedao-vault/apk-signing.jks + apk-signing.pass（四部书共用同一证书）
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)

TC=${TOOLCHAIN:-$HOME/.daokedao-vault/toolchain}
BT=${BUILD_TOOLS:-$TC/android-14}
AJAR=${ANDROID_JAR:-$TC/android-35/android.jar}
JAVA_HOME=${JAVA_HOME:-$(ls -d "$TC"/jdk-11*/ 2>/dev/null | head -1)}
VAULT=${VAULT:-$HOME/.daokedao-vault}
KS="${APK_KS:-/home/user/keys/runze-release.keystore}"
APK_PASS=${APK_PASS:-runze2026}
VERNAME=1.2.0
VERCODE=12001

if [ ! -x "$BT/aapt2" ] || [ ! -f "$AJAR" ] || [ -z "${JAVA_HOME:-}" ]; then
  echo "工具链缺失，先跑：bash ../scripts/setup-toolchain.sh" >&2
  exit 1
fi

echo "== 0/6 assets =="
[ -f assets/book.html ] || python3 prepare-assets.py

echo "== 1/6 资源编译 =="
rm -rf build dist && mkdir -p build/gen build/classes build/dex dist
"$BT/aapt2" compile --dir res -o build/res.zip

echo "== 2/6 资源链接 =="
"$BT/aapt2" link -o build/base.apk \
  -I "$AJAR" \
  --manifest AndroidManifest.xml \
  -A assets \
  --java build/gen \
  -R build/res.zip \
  --auto-add-overlay \
  --target-sdk-version 34 \
  --version-code "$VERCODE" --version-name "$VERNAME"

echo "== 3/6 编译 java =="
"${JAVA_HOME}bin/javac" -encoding UTF-8 -source 8 -target 8 \
  -bootclasspath "$AJAR" -classpath "$AJAR" \
  -d build/classes \
  build/gen/com/daokedao/tanjing/R.java \
  java/com/daokedao/tanjing/MainActivity.java 2>&1 | grep -v "^警告\|warning:" || true

echo "== 4/6 生成 dex =="
"$BT/d8" --min-api 21 --lib "$AJAR" --output build/dex \
  $(find build/classes -name '*.class')

echo "== 5/6 打包与对齐 =="
cp build/base.apk build/withdex.apk
(cd build/dex && zip -q -j ../withdex.apk classes.dex)
"$BT/zipalign" -f -p 4 build/withdex.apk build/aligned.apk

echo "== 6/6 签名 =="
if [ ! -f "$KS" ]; then
  echo "  生成签名密钥：$KS"
  mkdir -p "$VAULT"; chmod 700 "$VAULT" 2>/dev/null || true
  [ -f "$KP" ] || { head -c 24 /dev/urandom | base64 | tr -d '/+=' | cut -c1-20 > "$KP"; chmod 600 "$KP"; }
  "${JAVA_HOME}bin/keytool" -genkeypair -v -keystore "$KS" -alias daokedao \
    -keyalg RSA -keysize 2048 -validity 10950 \
    -storepass "$(cat "$KP")" -keypass "$(cat "$KP")" \
    -dname "CN=DaoKeDao Reader, O=DaoKeDao, C=CN" >/dev/null 2>&1
  chmod 600 "$KS"
fi
"$BT/apksigner" sign \
  --ks "$KS" --ks-pass "pass:$APK_PASS" --key-pass "pass:$APK_PASS" \
  --min-sdk-version 21 \
  --out "dist/道可道-坛经-$VERNAME.apk" build/aligned.apk
"$BT/apksigner" verify --min-sdk-version 21 "dist/道可道-坛经-$VERNAME.apk" | head -5

ls -la "dist/道可道-坛经-$VERNAME.apk"
echo "✓ 完成：dist/道可道-坛经-$VERNAME.apk"
