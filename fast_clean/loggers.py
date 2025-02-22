"""
Модуль, содержащий функционал, связанный логированием.
"""

import logging
import logging.config
from pathlib import Path

import yaml


def use_logging(base_dir: Path) -> None:
    """
    Применяем настройки логирования.
    """
    files = ['.logging.dev.yaml', '.logging.yaml']
    for file in files:
        ls_file = base_dir / file
        if ls_file.exists():
            with open(ls_file, 'rt') as f:
                config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
            break
    else:
        print(f'Missing configuration logging files: {", ".join(files)}')
        exit(0)
