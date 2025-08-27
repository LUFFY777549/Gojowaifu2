import importlib
import logging
from TEAMZYRO.modules import ALL_MODULES
from TEAMZYRO import app  # Pyrogram client import

# === Logger ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    # Load all modules
    for module_name in ALL_MODULES:
        importlib.import_module("TEAMZYRO.modules." + module_name)
    LOGGER.info("✅ All Features Loaded Baby🥳...")

    # Start Pyrogram bot
    app.run()

    LOGGER.info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎ MADE BY GOJOXNETWORK ☠︎︎ \n╚═════ஜ۩۞۩ஜ════╝"
    )


if __name__ == "__main__":
    main()