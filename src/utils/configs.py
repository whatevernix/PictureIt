import yaml


def yaml_open(file) -> dict:
    return yaml.safe_load(open(file))
