import json
from pathlib import Path

with open(Path(__file__).parent / "prompts.json") as _f:
    PROMPTS = json.load(_f)
