import yaml
from pathlib import Path
from types import SimpleNamespace

bot_template_path = Path("bot_template.yaml")


with bot_template_path.open("r") as f:
    data = yaml.safe_load(f)
print(data)
