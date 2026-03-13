import sys
from activation_mgr import generate_token

def main():
    print("=======================================================")
    print("    MagxxicVOT Advanced Email Sorter - Admin Kit")
    print("=======================================================")
    print()

    if len(sys.argv) > 1:
        hwid = sys.argv[1]
    else:
        hwid = input("Enter User HWID: ").strip()

    if not hwid:
        print("Error: HWID cannot be empty.")
        return

    token = generate_token(hwid)
    print(f"\nGenerated Token for HWID [{hwid}]:")
    print(f">>> {token} <<<")
    print("\nProvide this token to the user for activation.")

if __name__ == "__main__":
    main()
