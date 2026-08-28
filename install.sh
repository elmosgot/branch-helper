#!/usr/bin/env bash
set -euo pipefail

sudo install -Dm755 bin/branch-helper /usr/local/bin/branch-helper
sudo rm -rf /usr/local/share/branch-helper
sudo mkdir -p /usr/local/share/branch-helper
sudo cp -r branch_helper /usr/local/share/branch-helper/
sudo find /usr/local/share/branch-helper -type d -exec chmod 755 {} +
sudo find /usr/local/share/branch-helper -type f -exec chmod 644 {} +

echo "Installed branch-helper to /usr/local/bin/branch-helper"
