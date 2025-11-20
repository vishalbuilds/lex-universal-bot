import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Now import and run
from src.bot_engine.universal_bot_orchestrator import CreateUniversalBot

if __name__ == "__main__":
    c = CreateUniversalBot()
    print(c)
