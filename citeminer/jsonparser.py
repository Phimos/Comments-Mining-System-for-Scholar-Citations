import json


def parse_json_config(config_path: str):
    assert config_path.endswith(".json")
    with open(config_path) as f:
        config = json.load(f)
    print(config)
    return config


if __name__ == "__main__":
    a = parse_json_config("basic.json")
