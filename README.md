# MagxxicVOT Advanced Email Sorter

MagxxicVOT Advanced Email Sorter is a professional-grade tool designed for high-accuracy categorization of email lists. Unlike basic sorters that rely solely on domain names, this tool performs **asynchronous MX record lookups** to identify the underlying mail service provider for any domain.

## Key Features

- **MX-Based Provider Identification**: Accurately identifies providers like Google Workspace, Office 365, Yahoo, AOL, and various Chinese providers (QQ, Aliyun, Sina, Netease) even when custom domains are used.
- **Support for Generic Webmail**: Categorizes domains using Zimbra, Roundcube, cPanel, Plesk, and DirectAdmin into dedicated groups.
- **High-Performance Asynchronous Processing**: Built with `asyncio` and `aiodns` for rapid processing of large email lists with minimal resource usage.
- **Professional GUI**: A sleek dark-themed Tkinter interface for real-time visualization of sorting statistics and progress tracking.
- **CLI Mode**: A lightweight script for command-line environments.
- **Modular Configuration**: Easy-to-maintain provider mapping in `provider_config.py`.
- **Efficient Resource Management**: Dynamically creates output files only when relevant emails are found.

## Project Structure

- `magxxic_sorter_gui.py`: The main GUI application.
- `email_sorter.py`: The CLI version of the tool.
- `sorter_utils.py`: Core asynchronous sorting and provider identification logic.
- `provider_config.py`: Centralized mapping of MX record patterns to provider names.
- `activation_mgr.py`: Handles HWID generation and token validation.
- `admin_activation_kit.py`: Tool for administrators to generate tokens.

## Activation

Upon first use, the application will prompt for an activation token.
1.  Launch the application.
2.  Copy the displayed **HWID**.
3.  Provide the HWID to your administrator to receive an **Activation Token**.
4.  Enter the token to unlock the application.

## Requirements

- Python 3.8+
- `aiodns`: For asynchronous DNS queries.
- `pycares`: A dependency of aiodns.
- `tkinter`: Standard Python library for GUI (usually included with Python).

## Setup Instructions

### 1. Install Dependencies

**For Windows Users:**
Simply double-click the `setup.bat` file. This will automatically install the required libraries and launch the GUI.

**Manual Installation (All Platforms):**
Ensure you have the required libraries installed via pip:

```bash
pip install aiodns pycares
```

*Note: On some Linux distributions, you might need to install `python3-tk` for the GUI to work.*

### 2. Prepare Your Email List

Create a text file (e.g., `emails.txt`) containing one email address per line.

### 3. Usage

#### Using the GUI (Recommended)

Run the GUI script:

```bash
python magxxic_sorter_gui.py
```

1.  **Browse** for your `Mail File`.
2.  Select an **Output Dir** (defaults to a `sorted_output` folder in the current directory).
3.  Click **START** to begin sorting.
4.  View real-time statistics and progress in the table.

#### Using the CLI

Run the CLI script:

```bash
python email_sorter.py
```

By default, it looks for `emails.txt` and saves results to `sorted_output/`. You can modify these paths in the `main()` function of `email_sorter.py`.

## Sorting Categories

The tool categorizes emails into several groups, including:
- **Major Providers**: Gmail, Office365, Yahoo, Aol, Protonmail, Naver, etc.
- **Chinese Providers**: QQ, Netease, Aliyun, Sina, 21cn, 263.
- **Hosting/Webmail**: Zimbra, Roundcube, Webmail (cPanel, Plesk, etc.).
- **Security Filters**: MessageLabs, Mimecast, Proofpoint.
- **Generic**: Others(MX) - identified as having mail servers but unknown provider; Others(No_MX) - no valid MX records found.
- **Unknown**: Invalid email formats.

## License

This project is for educational and professional use. Please ensure you comply with all relevant regulations regarding email processing.
