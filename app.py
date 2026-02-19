import os
import random
from twilio.rest import Client as TwilioClient
import vonage
import boto3
import requests
import plivo
from plivo.exceptions import PlivoRestError
import messagebird
import telnyx
from telesign.messaging import MessagingClient
import pyfiglet
import socks
import socket

# --- Proxy Management ---

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.enabled = False
        self.current_index = 0

    def load_proxies(self, filepath):
        try:
            with open(filepath, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(self.proxies)} proxies from {filepath}")
        except Exception as e:
            print(f"Error loading proxies: {e}")

    def validate_proxies(self):
        if not self.proxies:
            print("No proxies to validate.")
            return
        active_proxies = []
        print("Validating proxies... this may take a while.")
        for proxy in self.proxies:
            if self.check_proxy(proxy):
                active_proxies.append(proxy)
                print(f"Proxy {proxy} is active.")
            else:
                print(f"Proxy {proxy} is dead.")
        self.proxies = active_proxies
        print(f"Validation complete. {len(self.proxies)} active proxies remain.")

    def check_proxy(self, proxy_str):
        try:
            # Simplified check using requests with a short timeout
            proxy_url = proxy_str if "://" in proxy_str else f"socks5://{proxy_str}"
            proxies = {"http": proxy_url, "https": proxy_url}
            response = requests.get("https://api.ipify.org", proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_next_proxy_url(self):
        if not self.enabled or not self.proxies:
            return None
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy if "://" in proxy else f"socks5://{proxy}"

proxy_manager = ProxyManager()

def get_current_ip(proxy_url=None):
    try:
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        response = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- Environment Variable Setup ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_PHONE_NUMBER = os.environ.get("VONAGE_PHONE_NUMBER")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
PLIVO_AUTH_ID = os.environ.get("PLIVO_AUTH_ID")
PLIVO_AUTH_TOKEN = os.environ.get("PLIVO_AUTH_TOKEN")
PLIVO_PHONE_NUMBER = os.environ.get("PLIVO_PHONE_NUMBER")
MESSAGEBIRD_API_KEY = os.environ.get("MESSAGEBIRD_API_KEY")
MESSAGEBIRD_PHONE_NUMBER = os.environ.get("MESSAGEBIRD_PHONE_NUMBER")
TELNYX_API_KEY = os.environ.get("TELNYX_API_KEY")
TELNYX_PHONE_NUMBER = os.environ.get("TELNYX_PHONE_NUMBER")
TELESIGN_CUSTOMER_ID = os.environ.get("TELESIGN_CUSTOMER_ID")
TELESIGN_API_KEY = os.environ.get("TELESIGN_API_KEY")
TELESIGN_PHONE_NUMBER = os.environ.get("TELESIGN_PHONE_NUMBER")

# --- Client Initialization ---
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]) else None
vonage_client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET) if all([VONAGE_API_KEY, VONAGE_API_SECRET]) else None
sns_client = boto3.client('sns', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION_NAME) if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME]) else None
plivo_client = plivo.RestClient(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN) if all([PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN]) else None
messagebird_client = messagebird.Client(MESSAGEBIRD_API_KEY) if MESSAGEBIRD_API_KEY else None
if TELNYX_API_KEY:
    telnyx.api_key = TELNYX_API_KEY
telesign_client = MessagingClient(TELESIGN_CUSTOMER_ID, TELESIGN_API_KEY) if all([TELESIGN_CUSTOMER_ID, TELESIGN_API_KEY]) else None

# --- Link Tracking ---

track_links = False
base_tracking_url = ""

def shorten_url(url):
    try:
        # Use TinyURL API for simple shortening
        response = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
        if response.status_code == 200:
            return response.text
        return url
    except:
        return url

def generate_tracked_link(base_url, recipient):
    if not base_url:
        return ""
    import urllib.parse
    # URL encode the recipient to handle '+' etc.
    safe_recipient = urllib.parse.quote(recipient)
    separator = "&" if "?" in base_url else "?"
    tracked_url = f"{base_url}{separator}to={safe_recipient}"
    return shorten_url(tracked_url)

# --- Core Functions ---

def check_twilio_api(proxy=None):
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
            return "Twilio credentials not configured."

        client = twilio_client
        if proxy:
            from twilio.http.http_client import TwilioHttpClient
            http_client = TwilioHttpClient(proxy={'http': proxy, 'https': proxy})
            client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, http_client=http_client)

        client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        return f"Twilio API is working.{' (via proxy)' if proxy else ''}"
    except Exception as e:
        return f"Twilio API check failed: {e}"

def check_vonage_api(proxy=None):
    try:
        if not all([VONAGE_API_KEY, VONAGE_API_SECRET]):
            return "Vonage credentials not configured."

        client = vonage_client
        if proxy:
            from vonage import Client
            client = Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy

        client.account.get_balance()

        if proxy:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

        return f"Vonage API is working.{' (via proxy)' if proxy else ''}"
    except Exception as e:
        if proxy:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
        return f"Vonage API check failed: {e}"

def send_sms_twilio(phone_number, message, proxy=None):
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            raise ConnectionError("Twilio credentials or phone number not configured.")

        client = twilio_client
        if proxy:
            from twilio.http.http_client import TwilioHttpClient
            http_client = TwilioHttpClient(proxy={'http': proxy, 'https': proxy})
            client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, http_client=http_client)
            print(f"Using proxy: {proxy}")

        msg = client.messages.create(to=phone_number, from_=TWILIO_PHONE_NUMBER, body=message)
        print(f"Twilio SMS sent to {phone_number}, SID: {msg.sid}")
    except Exception as e:
        print(f"Twilio SMS failed: {e}")

def send_sms_vonage(phone_number, message, proxy=None):
    try:
        if not all([VONAGE_API_KEY, VONAGE_API_SECRET, VONAGE_PHONE_NUMBER]):
            raise ConnectionError("Vonage credentials or phone number not configured.")

        client = vonage_client
        if proxy:
            # For newer vonage versions
            from vonage import Client
            client = Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
            # Vonage doesn't have an easy way to set proxy in the constructor easily without more boilerplate
            # But we can try setting environment variables for requests which it uses
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            print(f"Using proxy: {proxy}")

        response = client.sms.send_message({'from': VONAGE_PHONE_NUMBER, 'to': phone_number, 'text': message})

        if proxy:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

        if response["messages"][0]["status"] == "0":
            print(f"Vonage SMS sent to {phone_number}, Message ID: {response['messages'][0]['message-id']}")
        else:
            print(f"Vonage SMS failed: {response['messages'][0]['error-text']}")
    except Exception as e:
        print(f"Vonage SMS failed: {e}")
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)

def send_sms_aws_sns(phone_number, message, proxy=None):
    try:
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME]):
            raise ConnectionError("AWS SNS credentials not configured.")

        client = sns_client
        if proxy:
            from botocore.config import Config
            config = Config(proxies={'http': proxy, 'https': proxy})
            client = boto3.client('sns', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION_NAME, config=config)
            print(f"Using proxy: {proxy}")

        response = client.publish(PhoneNumber=phone_number, Message=message, MessageAttributes={'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}})
        print(f"AWS SNS SMS sent to {phone_number}, Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"AWS SNS SMS failed: {e}")

def send_sms_plivo(phone_number, message, proxy=None):
    try:
        if not all([PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN, PLIVO_PHONE_NUMBER]):
            raise ConnectionError("Plivo credentials or phone number not configured.")

        client = plivo_client
        if proxy:
            # Plivo uses 'proxydict' instead of 'proxies'
            client = plivo.RestClient(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN, proxydict={'http': proxy, 'https': proxy})
            print(f"Using proxy: {proxy}")

        response = client.messages.create(src=PLIVO_PHONE_NUMBER, dst=phone_number, text=message)
        print(f"Plivo SMS sent. Response: {response}")
    except PlivoRestError as e:
        print(f"Plivo SMS failed: {e}")

def send_sms_messagebird(phone_number, message, proxy=None):
    try:
        if not all([MESSAGEBIRD_API_KEY, MESSAGEBIRD_PHONE_NUMBER]):
            raise ConnectionError("Messagebird credentials or phone number not configured.")

        client = messagebird_client
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            client = messagebird.Client(MESSAGEBIRD_API_KEY)
            print(f"Using proxy: {proxy}")

        response = client.message_create(MESSAGEBIRD_PHONE_NUMBER, phone_number, message)
        print(f"Messagebird SMS sent. Response: {response}")

        if proxy:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
    except messagebird.client.ErrorException as e:
        print(f"Messagebird SMS failed: {e}")
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)

def send_sms_telnyx(phone_number, message, proxy=None):
    try:
        if not all([TELNYX_API_KEY, TELNYX_PHONE_NUMBER]):
            raise ConnectionError("Telnyx API key or phone number not configured.")

        if proxy:
            telnyx.proxy = proxy
            print(f"Using proxy: {proxy}")
        else:
            telnyx.proxy = None

        telnyx.Message.create(to=phone_number, from_=TELNYX_PHONE_NUMBER, text=message)
        print(f"Telnyx SMS sent to {phone_number}")
    except telnyx.error.APIError as e:
        print(f"Telnyx SMS failed: {e}")

def send_sms_telesign(phone_number, message, proxy=None):
    try:
        if not all([TELESIGN_CUSTOMER_ID, TELESIGN_API_KEY]):
            raise ConnectionError("Telesign credentials not configured.")

        client = telesign_client
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            client = MessagingClient(TELESIGN_CUSTOMER_ID, TELESIGN_API_KEY)
            print(f"Using proxy: {proxy}")

        response = client.message(phone_number, message, "ARN")

        if proxy:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

        if response.ok:
            print(f"Telesign SMS sent. Reference ID: {response.json['reference_id']}")
        else:
            print(f"Telesign SMS failed: {response.body}")
    except Exception as e:
        print(f"Telesign SMS failed: {e}")
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)

def send_sms_textbelt(phone_number, message, proxy=None):
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        if proxy:
            print(f"Using proxy: {proxy}")
        response = requests.post('https://textbelt.com/text', {'phone': phone_number, 'message': message, 'key': 'textbelt'}, proxies=proxies).json()
        if response.get("success"):
            print(f"TextBelt SMS sent to {phone_number}")
        else:
            print(f"TextBelt SMS failed: {response.get('error')}")
    except Exception as e:
        print(f"TextBelt SMS failed: {e}")

def generate_phone_number():
    number = f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
    print(f"Generated Phone Number: {number}")

def check_phone_number_stub(phone_number):
    status = random.choice(["Live", "Dead"])
    print(f"Phone number {phone_number} is {status}.")
    return status

def filter_carrier_stub(phone_number):
    carrier = random.choice(["AT&T", "Verizon", "T-Mobile", "Sprint"])
    print(f"Carrier for {phone_number} is {carrier}.")

def check_and_filter_carrier_stub(phone_number):
    if check_phone_number_stub(phone_number) == "Live":
        filter_carrier_stub(phone_number)

# --- CLI Helper Functions ---

def get_sms_input():
    """Prompts user for phone numbers (manual or file) and a message."""
    phone_numbers = []
    while True:
        choice = input("Enter 'M' for manual entry or 'F' to load from a file: ").upper()
        if choice == 'M':
            phone_numbers_str = input("Enter phone number(s) (comma-separated): ")
            phone_numbers = [num.strip() for num in phone_numbers_str.split(',')]
            break
        elif choice == 'F':
            filepath = input("Enter the path to your .txt file: ")
            try:
                with open(filepath, 'r') as f:
                    # Read numbers line-by-line
                    phone_numbers = [line.strip() for line in f if line.strip()]
                print(f"Successfully loaded {len(phone_numbers)} numbers from {filepath}")
                break
            except FileNotFoundError:
                print(f"Error: File not found at '{filepath}'. Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Invalid choice. Please enter 'M' or 'F'.")

    message = input("Enter message: ")
    return phone_numbers, message

def get_phone_number_input():
    """Prompts user for a single phone number."""
    return input("Enter phone number to check: ")

def configure_proxy():
    global proxy_manager
    while True:
        print("\n--- Proxy Settings ---")
        print(f"Status: {'ENABLED' if proxy_manager.enabled else 'DISABLED'}")
        print(f"Proxies loaded: {len(proxy_manager.proxies)}")
        print("1. Enable/Disable Proxy")
        print("2. Load Proxies from File")
        print("3. Validate Proxies")
        print("4. Back to Main Menu")
        choice = input("Select: ")
        if choice == '1':
            proxy_manager.enabled = not proxy_manager.enabled
            print(f"Proxy is now {'ENABLED' if proxy_manager.enabled else 'DISABLED'}.")
        elif choice == '2':
            filepath = input("Enter proxy list path (SOCKS5): ")
            proxy_manager.load_proxies(filepath)
        elif choice == '3':
            proxy_manager.validate_proxies()
        elif choice == '4':
            break

def configure_tracking():
    global track_links, base_tracking_url
    while True:
        print("\n--- Link Tracking Settings ---")
        print(f"Status: {'ENABLED' if track_links else 'DISABLED'}")
        print(f"Base URL: {base_tracking_url}")
        print("1. Enable/Disable Link Tracking")
        print("2. Set Base Tracking URL")
        print("3. Back to Main Menu")
        choice = input("Select: ")
        if choice == '1':
            track_links = not track_links
            print(f"Link Tracking is now {'ENABLED' if track_links else 'DISABLED'}.")
        elif choice == '2':
            base_tracking_url = input("Enter Base Tracking URL: ")
        elif choice == '3':
            break

def print_menu():
    """Prints the main menu to the console."""
    os.system('cls' if os.name == 'nt' else 'clear')

    # ASCII Art Title
    ascii_art_title = pyfiglet.figlet_format("MagxxicVOT SMS", font="slant")
    print(f"\033[1;35m{ascii_art_title}\033[0m")

    by_line = "Note : I am not responsible for illegal use of the software"
    print(f"\033[36m{' ' * ((82 - len(by_line)) // 2)}{by_line}\033[0m")
    print("\033[32m" + "┌" + "─" * 80 + "┐" + "\033[0m")

    options = [
        ("1", "Nexmo Bulk SMS Sender"), ("9", "Telnyx Bulk SMS Sender"),
        ("2", "Twilio Bulk SMS Sender"), ("10", "Telesign Bulk SMS Sender"),
        ("3", "Plivo Bulk SMS Sender"), ("11", "Amazon SNS Bulk SMS Sender"),
        ("4", "Messagebird Bulk SMS Sender"), ("12", "Phone Number Generator"),
        ("7", "TextBelt Bulk SMS Sender"), ("13", "Phone Checker [Live/Die]"),
        ("8", "Nexmo Api checker"), ("14", "Phone checker Filter Carrier"),
        ("17", "Proxy Settings"), ("15", "Option 13 + 14"),
        ("18", "Link Tracking Settings"), ("16", "Twilio api Checker"),
        ("19", "Show My IP"), ("", ""),
    ]

    num_items_per_col = len(options) // 2
    for i in range(num_items_per_col):
        left_num, left_desc = options[i]
        right_num, right_desc = options[i + num_items_per_col]

        if not left_desc and not right_desc:
            continue

        left_color = "\033[95m" if left_num == "7" else "\033[94m"
        right_color = "\033[95m" if right_num in ["14", "15"] else "\033[96m"

        left_part = f"{left_color}[ {left_num.ljust(2)}] {left_desc.ljust(30)}\033[0m" if left_desc else " " * 36
        right_part = f"{right_color}[ {right_num.ljust(2)}] {right_desc.ljust(30)}\033[0m" if right_desc else ""

        print(f"\033[32m│\033[0m {left_part} {right_part} \033[32m│\033[0m")

    print("\033[32m" + "└" + "─" * 80 + "┘" + "\033[0m")

def main():
    """Main function to run the CLI application."""

    def send_sms_to_multiple(sms_function):
        """Gets input and sends SMS to multiple numbers."""
        phone_numbers, message = get_sms_input()
        for number in phone_numbers:
            current_message = message
            if track_links and base_tracking_url:
                tracked_link = generate_tracked_link(base_tracking_url, number)
                current_message = f"{message} {tracked_link}"

            proxy = proxy_manager.get_next_proxy_url()
            sms_function(number, current_message, proxy=proxy)

    actions = {
        '1': lambda: send_sms_to_multiple(send_sms_vonage),
        '2': lambda: send_sms_to_multiple(send_sms_twilio),
        '3': lambda: send_sms_to_multiple(send_sms_plivo),
        '4': lambda: send_sms_to_multiple(send_sms_messagebird),
        '7': lambda: send_sms_to_multiple(send_sms_textbelt),
        '8': lambda: print(check_vonage_api(proxy_manager.get_next_proxy_url() if proxy_manager.enabled else None)),
        '9': lambda: send_sms_to_multiple(send_sms_telnyx),
        '10': lambda: send_sms_to_multiple(send_sms_telesign),
        '11': lambda: send_sms_to_multiple(send_sms_aws_sns),
        '12': generate_phone_number,
        '13': lambda: check_phone_number_stub(get_phone_number_input()),
        '14': lambda: filter_carrier_stub(get_phone_number_input()),
        '15': lambda: check_and_filter_carrier_stub(get_phone_number_input()),
        '16': lambda: print(check_twilio_api(proxy_manager.get_next_proxy_url() if proxy_manager.enabled else None)),
        '17': configure_proxy,
        '18': configure_tracking,
        '19': lambda: print(f"Your IP: {get_current_ip(proxy_manager.get_next_proxy_url() if proxy_manager.enabled else None)}"),
    }

    while True:
        print_menu()
        choice = input("Select : ")
        if choice.lower() in ['exit', 'quit']:
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option. Please try again.")

        input("\nPress Enter to return to the menu...")

if __name__ == '__main__':
    main()
