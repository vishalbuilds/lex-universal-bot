import yaml
from pathlib import Path
from types import SimpleNamespace

# Get the path relative to this file's location
bot_template_path = Path(__file__).parent.parent.parent / "bot_template.yaml"


def to_ns(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: to_ns(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [to_ns(i) for i in d]
    return d


with bot_template_path.open("r") as f:
    data = yaml.safe_load(f)

bot_config = to_ns(data["bot"])


# print(bot_config)
