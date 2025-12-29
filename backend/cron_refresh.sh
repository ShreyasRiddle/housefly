#!/bin/bash
# Daily cron job script for Housefly data refresh
# Add to crontab with: 0 2 * * * /path/to/housefly/backend/cron_refresh.sh

cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python scripts/run_refresh.py >> logs/cron_refresh.log 2>&1

