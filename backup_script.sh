#!/bin/bash

# Configuration
BACKUP_DIR="$HOME/tgpc_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Files to back up
IMPORTANT_FILES=(
    "$PROJECT_DIR/rx.json"
    "$PROJECT_DIR/data/raw/"
)

# Create backup
for file in "${IMPORTANT_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo "Backing up $file..."
        cp -r "$file" "${BACKUP_DIR}/$(basename "$file")_${TIMESTAMP}"
    fi
done

echo "Backup completed in $BACKUP_DIR"

# Keep only the last 5 backups
ls -t "$BACKUP_DIR" | tail -n +6 | xargs -I {} rm -rf "$BACKUP_DIR/{}"
