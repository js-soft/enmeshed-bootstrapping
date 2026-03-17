#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

./build-app0.sh install

adb reverse tcp:8090 tcp:8090
adb reverse tcp:8092 tcp:8092
adb reverse tcp:9099 tcp:9099