import json
import os

CONFIG_FILE = "config.json"


def create_default_config():
    print(f"create default config")
    with open(CONFIG_FILE, mode="w") as f:
        default_config = {"data_directory": os.path.join(os.getcwd(), "data")}
        json.dump(default_config, f)


if not os.path.isfile(CONFIG_FILE):
    print(f"missing config file")
    create_default_config()
else:
    with open(CONFIG_FILE, "r") as f:
        try:
            json.load(f)
            print(f"config file ok")
        except ValueError as e:
            print(f"config file error: {str(e)}")
            create_default_config()


def get_value(key):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        return config.get(key)


def set_value(key, value):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        # print(f"config 1: {config}")
        config[key] = value
        # print(f"config 2: {config}")
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
