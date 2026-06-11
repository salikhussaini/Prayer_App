import os
import subprocess
import platform
import logging
from src.core.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

def check_for_updates():
    """Checks if updates are available via git and runs the update script if so.
    
    This is primarily intended for Linux/Raspberry Pi deployments.
    On Windows, it will log a warning as .sh scripts aren`t natively supported.
    """
    if platform.system() == "Windows":
        logger.debug("Auto-update check skipped on Windows.")
        return False

    update_script = PROJECT_ROOT / "src" / "scripts" / "update_app.sh"
    
    if not update_script.exists():
        logger.warning(f"Update script not found at {update_script}")
        return False

    try:
        # Step 1: Fetch to see if there are changes
        subprocess.run(["git", "fetch"], check=True, capture_output=True, cwd=PROJECT_ROOT)
        
        # Step 2: Compare LOCAL vs REMOTE
        local = subprocess.check_output(["git", "rev-parse", "@"], cwd=PROJECT_ROOT).strip().decode('utf-8')
        remote = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=PROJECT_ROOT).strip().decode('utf-8')
        
        if local != remote:
            logger.info("Updates detected! Triggering update_app.sh...")
            # Run the script in the background and exit the current process
            # The script will handle pulling and restarting
            subprocess.Popen(["bash", str(update_script)], cwd=PROJECT_ROOT)
            return True
            
        logger.debug("No updates found.")
        return False
        
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return False
