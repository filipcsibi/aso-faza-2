import sys
import box
import yaml
from pathlib import Path

CONFIG_ABSOLUTE_PATH = Path.home() / 'proiect-aso' / 'config' / 'config.yml'

try:
    with open(CONFIG_ABSOLUTE_PATH, 'r', encoding='utf8') as ymlfile:
        cfg = box.Box(yaml.safe_load(ymlfile))
except Exception as e:
    print(f"Error loading config: {e}", file=sys.stderr)
    sys.exit(1)
