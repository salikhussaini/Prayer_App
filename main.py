import sys
import src.core as core
from src.gui import MainWindow

if __name__ == "__main__":
    # Initialize logging
    core.setup_logging()
    
    # Check for updates (Linux/Pi specific)
    # If an update is found, this will trigger the .sh script and we should exit
    if core.check_for_updates():
        print("Update triggered. Restarting...")
        sys.exit(0)

    app = MainWindow()
    app.mainloop()