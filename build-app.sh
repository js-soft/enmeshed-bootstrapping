#!/usr/bin/env bash
#
# Build, install and run the enmeshed Flutter app on an Android emulator/device.
#
# Usage:
#   ./build-app.sh clone                # clone repo + melos bootstrap
#   ./build-app.sh build                # build debug APK
#   ./build-app.sh install [-d device]  # install APK via adb (uninstalls first)
#   ./build-app.sh wipe [-d device]     # uninstall app + clear all data
#   ./build-app.sh run [-d device]      # launch app via adb
#   ./build-app.sh all [-d device]      # clone + build + install + run
#
# Options (install/run/all only):
#   -d <device>    Target device serial (from `adb devices`). Uses default adb device if omitted.
#
# Environment overrides:
#   BASE_URL       (default: http://localhost:8090)
#   CLIENT_ID      (default: test)
#   CLIENT_SECRET  (default: test)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure dart global packages (melos) are on PATH
export PATH="$HOME/.pub-cache/bin:$PATH"

# --- Config (override via env) ---
BASE_URL="${BASE_URL:-http://localhost:8090}"
CLIENT_ID="${CLIENT_ID:-test}"
CLIENT_SECRET="${CLIENT_SECRET:-test}"

REPO_DIR="$SCRIPT_DIR/repos/nmshd_app"
APP_DIR="$REPO_DIR/apps/enmeshed"
APK_PATH="$APP_DIR/build/app/outputs/flutter-apk/app-debug.apk"
PACKAGE="eu.enmeshed.app"

log() { echo "-- $*"; }

parse_device_opt() {
    ADB=(adb)
    local OPTIND=1
    while getopts "d:" opt; do
        case "$opt" in
            d) ADB=(adb -s "$OPTARG") ;;
            *) echo "Usage: $0 $1 [-d <device>]" >&2; exit 1 ;;
        esac
    done
}

# --- Subcommands ---

cmd_clone() {
    mkdir -p "$SCRIPT_DIR/repos"
    if [[ ! -d "$REPO_DIR" ]]; then
        log "Cloning enmeshed app to '$REPO_DIR'"
        git clone git@github.com:js-soft/nmshd_app.git "$REPO_DIR"
    else
        log "Found enmeshed app in '$REPO_DIR'"
    fi

    log "Running melos bootstrap"
    (cd "$REPO_DIR" && melos bootstrap)

    log "Generating translations"
    (cd "$REPO_DIR" && melos generate_translations)
}

cmd_build() {
    log "Writing config (baseUrl=$BASE_URL)"
    cat > "$APP_DIR/config.json" <<EOF
{
    "app_baseUrl": "$BASE_URL",
    "app_clientId": "$CLIENT_ID",
    "app_clientSecret": "$CLIENT_SECRET"
}
EOF

    log "Enabling cleartext traffic in debug manifest"
    cat > "$APP_DIR/android/app/src/debug/AndroidManifest.xml" <<MANIFEST
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="eu.enmeshed.app">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:usesCleartextTraffic="true" />
</manifest>
MANIFEST

    log "Building debug APK"
    (cd "$APP_DIR" && flutter build apk --debug --dart-define-from-file=config.json)

    log "APK: $APK_PATH"
}

cmd_wipe() {
    parse_device_opt wipe "$@"

    log "Uninstalling $PACKAGE (removing app + all data)"
    "${ADB[@]}" uninstall "$PACKAGE" || log "App was not installed, nothing to uninstall"
}

cmd_install() {
    parse_device_opt install "$@"

    if [[ ! -f "$APK_PATH" ]]; then
        echo "Error: APK not found at $APK_PATH — run './build-app.sh build' first" >&2
        exit 1
    fi

    cmd_wipe "$@"

    log "Installing APK via adb"
    "${ADB[@]}" install "$APK_PATH"

    log "Setting up adb reverse port forwarding (localhost:8090 -> host:8090)"
    "${ADB[@]}" reverse tcp:8090 tcp:8090
}

cmd_run() {
    parse_device_opt run "$@"

    log "Launching $PACKAGE"
    "${ADB[@]}" shell am start -n "$PACKAGE/.MainActivity"
}

cmd_all() {
    cmd_clone
    cmd_build
    cmd_install "$@"
    cmd_run "$@"
}

# --- Entry point ---

subcmd="${1:-}"
shift || true

case "$subcmd" in
    clone)   cmd_clone        ;;
    build)   cmd_build        ;;
    wipe)    cmd_wipe "$@"    ;;
    install) cmd_install "$@" ;;
    run)     cmd_run "$@"     ;;
    all)     cmd_all "$@"     ;;
    *)
        echo "Usage: $0 {clone|build|wipe|install|run|all}" >&2
        echo ""
        echo "  clone                Clone repo + melos bootstrap + generate translations"
        echo "  build                Build debug APK (writes config.json with BASE_URL)"
        echo "  wipe [-d device]     Uninstall app + clear all data"
        echo "  install [-d device]  Uninstall old app, then install APK (clean)"
        echo "  run [-d device]      Launch the app on emulator/device"
        echo "  all [-d device]      Run all steps in sequence"
        echo ""
        echo "Environment overrides:"
        echo "  BASE_URL=$BASE_URL"
        echo "  CLIENT_ID=$CLIENT_ID"
        echo "  CLIENT_SECRET=$CLIENT_SECRET"
        exit 1
        ;;
esac
