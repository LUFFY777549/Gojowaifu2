import importlib
import logging
from TEAMZYRO.modules import ALL_MODULES
from telegram.ext import Application

# === Logger ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

# === Bot Token ===
from TEAMZYRO.config import TOKEN   # apna token config.py me rakho

# === Application ===
application = Application.builder().token(TOKEN).build()


def main() -> None:
    # Load all modules
    for module_name in ALL_MODULES:
        importlib.import_module("TEAMZYRO.modules." + module_name)
    LOGGER.info("✅ All Features Loaded Baby🥳...")

    # Start bot
    application.run_polling(drop_pending_updates=True)

    LOGGER.info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎ MADE BY GOJOXNETWORK ☠︎︎ \n╚═════ஜ۩۞۩ஜ════╝"
    )


if __name__ == "__main__":
    main()