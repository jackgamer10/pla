import hashlib
import os
import platform
import subprocess

ACTIVATION_FILE = ".activation"
SECRET_SALT = "magxxicvot_v1_secure_salt"

def get_hwid():
    """Generates a unique hardware identifier based on system properties."""
    system = platform.system()
    hwid_base = ""

    try:
        if system == "Windows":
            # Use wmic to get CPU ID and Disk Serial
            cpu_id = subprocess.check_output("wmic cpu get processorid", shell=True).decode().split("\n")[1].strip()
            disk_id = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split("\n")[1].strip()
            hwid_base = f"{cpu_id}-{disk_id}"
        elif system == "Linux":
            # Use /etc/machine-id
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    hwid_base = f.read().strip()
            else:
                hwid_base = platform.node()
        else:
            hwid_base = platform.node() + platform.machine()
    except Exception:
        # Fallback to node name if something goes wrong
        hwid_base = platform.node()

    return hashlib.sha256(hwid_base.encode()).hexdigest()[:16].upper()

def generate_token(hwid):
    """Generates an activation token for a given HWID."""
    return hashlib.sha256((hwid + SECRET_SALT).encode()).hexdigest()[:24].upper()

def is_activated():
    """Checks if the application is already activated."""
    if not os.path.exists(ACTIVATION_FILE):
        return False

    try:
        with open(ACTIVATION_FILE, "r") as f:
            token = f.read().strip()

        hwid = get_hwid()
        expected_token = generate_token(hwid)
        return token == expected_token
    except Exception:
        return False

def activate(token):
    """Attempts to activate the application with a token."""
    hwid = get_hwid()
    expected_token = generate_token(hwid)

    if token == expected_token:
        with open(ACTIVATION_FILE, "w") as f:
            f.write(token)
        return True
    return False
