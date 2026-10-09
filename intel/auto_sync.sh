#!/usr/bin/env bash
# Cool Home (India) - Water Cooler Tender Intelligence Sync Daemon
# Usage: ./auto_sync.sh

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting automated tender sync..."
python3 auto_pipeline.py
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tender sync completed successfully."
