import hashlib
import sys

def generate_activation_key(token):
    salt = "MAGXXIC_VOT_SECRET_SALT_2024"
    return hashlib.sha256((token + salt).encode()).hexdigest()[:16].upper()

def main():
    print("--- MagxxicVOT SMS Key Generator ---")
    if len(sys.argv) > 1:
        token = sys.argv[1].strip().upper()
    else:
        token = input("Enter System Token: ").strip().upper()

    if not token:
        print("Error: Token cannot be empty.")
        return

    key = generate_activation_key(token)
    print(f"\n[+] System Token: {token}")
    print(f"[+] Activation Key: {key}")
    print("\nSend this Activation Key to the user.")

if __name__ == "__main__":
    main()
