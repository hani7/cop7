$ErrorActionPreference = 'Stop'

$androidDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $androidDir
$sdkRoot = if ($env:ANDROID_SDK_ROOT) { $env:ANDROID_SDK_ROOT } elseif ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$buildTools = Join-Path $sdkRoot 'build-tools\37.0.0'
$androidJar = Join-Path $sdkRoot 'platforms\android-35\android.jar'
$javaHome = Split-Path -Parent (Split-Path -Parent (Get-Command javac.exe).Source)
$keytool = Join-Path $javaHome 'bin\keytool.exe'
$javac = Join-Path $javaHome 'bin\javac.exe'
$jar = Join-Path $javaHome 'bin\jar.exe'
$manifest = Join-Path $androidDir 'app\src\main\AndroidManifest.xml'
$sourceDir = Join-Path $androidDir 'app\src\main\java'
$resourceDir = Join-Path $androidDir 'app\src\main\res'
$outputDir = Join-Path $androidDir 'app\build\outputs\apk\debug'
$workDir = Join-Path $androidDir 'app\build\local'
$generatedDir = Join-Path $workDir 'generated'
$classesDir = Join-Path $workDir 'classes'
$dexDir = Join-Path $workDir 'dex'
$compiledResources = Join-Path $workDir 'resources.zip'
$baseApk = Join-Path $workDir 'base.apk'
$alignedApk = Join-Path $workDir 'aligned.apk'
$keystore = Join-Path $projectDir '.runtime\android-debug.keystore'
$outputApk = Join-Path $outputDir 'copetrolite-technician-debug.apk'

foreach ($requiredPath in @(
    (Join-Path $buildTools 'aapt2.exe'),
    (Join-Path $buildTools 'd8.bat'),
    (Join-Path $buildTools 'zipalign.exe'),
    (Join-Path $buildTools 'apksigner.bat'),
    $androidJar,
    $javac,
    $jar,
    $keytool
)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Android build dependency not found: $requiredPath"
    }
}

New-Item -ItemType Directory -Force -Path $generatedDir, $classesDir, $dexDir, $outputDir, (Split-Path -Parent $keystore) | Out-Null

& (Join-Path $buildTools 'aapt2.exe') compile --dir $resourceDir -o $compiledResources
if ($LASTEXITCODE -ne 0) { throw 'Android resource compilation failed.' }

& (Join-Path $buildTools 'aapt2.exe') link --auto-add-overlay -o $baseApk -I $androidJar --manifest $manifest --java $generatedDir --min-sdk-version 23 --target-sdk-version 34 --version-code 1 --version-name 1.0 -R $compiledResources
if ($LASTEXITCODE -ne 0) { throw 'Android manifest/resource linking failed.' }

$javaFiles = @(
    Get-ChildItem $sourceDir, $generatedDir -Recurse -Filter '*.java' |
        ForEach-Object { $_.FullName }
)
& $javac -source 8 -target 8 -bootclasspath $androidJar -d $classesDir $javaFiles
if ($LASTEXITCODE -ne 0) { throw 'Android Java compilation failed.' }

$classFiles = @(Get-ChildItem $classesDir -Recurse -Filter '*.class' | ForEach-Object { $_.FullName })
& (Join-Path $buildTools 'd8.bat') --lib $androidJar --min-api 23 --output $dexDir $classFiles
if ($LASTEXITCODE -ne 0) { throw 'Android DEX compilation failed.' }

& $jar uf $baseApk -C $dexDir classes.dex
if ($LASTEXITCODE -ne 0) { throw 'Adding DEX to the APK failed.' }

& (Join-Path $buildTools 'zipalign.exe') -f 4 $baseApk $alignedApk
if ($LASTEXITCODE -ne 0) { throw 'APK alignment failed.' }

if (-not (Test-Path -LiteralPath $keystore)) {
    & $keytool -genkeypair -v -keystore $keystore -storepass android -alias androiddebugkey -keypass android -dname 'CN=Android Debug,O=Android,C=US' -keyalg RSA -keysize 2048 -validity 10000
    if ($LASTEXITCODE -ne 0) { throw 'Debug signing key generation failed.' }
}

& (Join-Path $buildTools 'apksigner.bat') sign --ks $keystore --ks-pass pass:android --key-pass pass:android --out $outputApk $alignedApk
if ($LASTEXITCODE -ne 0) { throw 'APK signing failed.' }

& (Join-Path $buildTools 'apksigner.bat') verify --verbose $outputApk
if ($LASTEXITCODE -ne 0) { throw 'APK signature verification failed.' }

Write-Host "APK created: $outputApk"
