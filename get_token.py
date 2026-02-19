import uuid
import socket
import hashlib

def get_token():
    # Generate a unique token based on machine info (HWID)
    # This must match the logic in app.py
    hwid = str(uuid.getnode()) + socket.gethostname()
    return hashlib.sha256(hwid.encode()).hexdigest()[:16].upper()

def main():
    print("--- MagxxicVOT SMS: Token Generator ---")
    token = get_token()
    print(f"\n[+] Your System Token: \033[1;32m{token}\033[0m")
    print("\n[!] Send this token to the Administrator to receive your Activation Key.")

if __name__ == "__main__":
    main()
