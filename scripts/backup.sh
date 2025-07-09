#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
mkdir -p $BACKUP_DIR

# Бэкап базы данных
docker exec cosplay_api sqlite3 /app/db.sqlite3 ".backup '/app/db_backup.sqlite3'"
docker cp cosplay_api:/app/db_backup.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Бэкап сгенерированных изображений
tar -czf $BACKUP_DIR/outputs_$DATE.tar.gz -C ./sd_server/outputs .