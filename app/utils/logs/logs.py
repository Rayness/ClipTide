# Copyright (C) 2025 Rayness
# This program is free software under GPLv3. See LICENSE for details.

from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging


def logs():
    log_dir = Path.home() / 'AppData' / 'Local' / 'ClipTide' / 'Logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    handler = RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=1024*1024,  # 1 MB
        backupCount=15  # Хранить 5 архивных копий
    )
    handler.setFormatter(formatter)

    logging.basicConfig(handlers=[handler], level=logging.INFO)