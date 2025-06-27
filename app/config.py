import yaml

def load_yaml_config(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)
config = None
def init():
    global config
    config = load_yaml_config('/config/config.yaml')

def getConfig():
    global config
    if config is None:
        init()
    return config
