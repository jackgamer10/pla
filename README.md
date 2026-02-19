# Magxxic Sender

This project is a command-line interface (CLI) application that allows you to send SMS messages to multiple recipients through various providers.

## Features

*   **Bulk SMS Sending:** Send SMS messages to a list of phone numbers, entered manually or loaded from a `.txt` file.
*   **Multi-Provider Support:**
    *   Twilio
    *   Vonage (formerly Nexmo)
    *   AWS SNS
    *   Plivo
    *   Messagebird
    *   Telnyx
    *   Telesign
    *   TextBelt (free tier)
*   **Beautiful CLI:** A user-friendly, menu-driven interface with a stylish ASCII art design.
*   **Utility Functions:**
    *   Check provider API status (Twilio, Vonage).
    *   Generate random phone numbers for testing.
    *   Check phone number status (mock implementation).
    *   Filter phone number carrier (mock implementation).

## Setup

1.  **License Activation:**
    When you first run the tool, it will generate a unique **System Token**.
    - Send this token to the Administrator to receive your **Activation Key**.
    - Create a file named `license.key` in the root directory.
    - Paste your Activation Key into the file.

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/multi-provider-sms-sender.git
    cd multi-provider-sms-sender
    ```

3.  **Install dependencies:**

    **On Windows:**
    Simply run the setup batch file:
    ```cmd
    setup.bat
    ```

    **On Linux/macOS:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set environment variables:**
    Create a `.env` file in the root of the project and add the API credentials for the services you intend to use.

    ```
    # Twilio
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_phone_number
    # ... (add other provider keys as needed)
    ```

## Usage

Run the application from your terminal:

**On Windows:**
```cmd
run.bat
```

**On Linux/macOS:**
```bash
python app.py
```

This will launch the interactive menu for the **Magxxic sender**.

```
    __  ___                      _         _____                __
   /  |/  /___ _____ __  ___  __(_)____   / ___/___  ____  ____/ /__  _____
  / /|_/ / __ `/ __ `/ |/_/ |/_/ / ___/   \__ \/ _ \/ __ \/ __  / _ \/ ___/
 / /  / / /_/ / /_/ />  <_>  </ / /__    ___/ /  __/ / / / /_/ /  __/ /
/_/  /_/\__,_/\__, /_/|_/_/|_/_/\___/   /____/\___/_/ /_/\__,_/\___/_/
             /____/

           Note : I am not responsible for illegal use of the software
┌────────────────────────────────────────────────────────────────────────────────┐
│ [ 1 ] Nexmo Bulk SMS Sender          [ 7 ] TextBelt Bulk SMS Sender       │
│ [ 9 ] Telnyx Bulk SMS Sender         [ 13] Phone Checker [Live/Die]       │
│ [ 2 ] Twilio Bulk SMS Sender         [ 8 ] Nexmo Api checker              │
│ [ 10] Telesign Bulk SMS Sender       [ 14] Phone checker Filter Carrier   │
│ [ 3 ] Plivo Bulk SMS Sender           │
│ [ 11] Amazon SNS Bulk SMS Sender     [ 15] Option 13 + 14                 │
│ [ 4 ] Messagebird Bulk SMS Sender     │
│ [ 12] Phone Number Generator         [ 16] Twilio api Checker             │
└────────────────────────────────────────────────────────────────────────────────┘
Select :
```

### Sending an SMS

When you select an SMS provider, you will be prompted to choose an input method:
*   **Manual Entry ('M'):** Type or paste phone numbers directly into the terminal, separated by commas.
*   **Load from File ('F'):** Provide the path to a `.txt` file containing the phone numbers.

#### Loading Numbers from a File

If you choose to load from a file, create a `.txt` file (e.g., `numbers.txt`) and list each phone number on a **new line**.

**Example `numbers.txt`:**
```
+1234567890
+1987654321
+15551234567
```

You will then be prompted to enter the path to this file. After the numbers are loaded, you will be asked for the message you wish to send.

To exit the application, type `exit` or `quit` at the main menu.

## Administrator Tools

### Key Generator

Administrators can use `keygen.py` to generate activation keys for users.
```bash
python keygen.py [SYSTEM_TOKEN]
```
