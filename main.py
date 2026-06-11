import sys
from src.gui.main_window import MainWindow
from src.core.utils import check_for_updates
from src.core.logger_config import setup_logging

if __name__ == "__main__":
    # Initialize logging
    setup_logging()
    
    # Check for updates (Linux/Pi specific)
    # If an update is found, this will trigger the .sh script and we should exit
    if check_for_updates():
        print("Update triggered. Restarting...")
        sys.exit(0)

    app = MainWindow()
    app.mainloop()