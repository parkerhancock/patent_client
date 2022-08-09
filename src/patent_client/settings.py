import os
from collections import defaultdict
from pathlib import Path

import yaml
from yankee.util import AttrDict

DEFAULT_SETTINGS_FILE = Path(__file__).parent / "default_settings.yml"
DEFAULT_SETTINGS = AttrDict.convert(yaml.safe_load(DEFAULT_SETTINGS_FILE.read_text()))


def load_settings_from_env():
    settings = defaultdict(dict)
    for k, v in os.environ.items():
        if not k.startswith("PATENT_CLIENT_"):
            continue
        k = k.replace("PATENT_CLIENT_", "")
        if "__" in k:
            section, k = k.split("__")
        else:
            section = "DEFAULT"
        settings[section][k] = v
    return settings


def load_user_settings():
    file = Path("~/.patent_client_config.yaml").expanduser()
    if file.exists():
        return yaml.safe_load(file.read_text())
    else:
        file.write_text(DEFAULT_SETTINGS_FILE.read_text())
        return dict()


def merge_settings(*settings):
    output = defaultdict(dict)
    for s in settings:
        for section, values in s.items():
            output[section] = {**output[section], **values}
    return output


def load_settings():
    return AttrDict.convert(
        merge_settings(
            DEFAULT_SETTINGS,
            load_user_settings(),
            load_settings_from_env(),
        )
    )
