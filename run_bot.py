import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Now import and run
from bot_engine.universal_bot_deployer import CreateUniversalBot

if __name__ == "__main__":
    c = CreateUniversalBot()
    print(c)
