# MagxxicVOT Advanced Email Sorter ULTRA

MagxxicVOT Advanced Email Sorter ULTRA is an elite-grade tool designed for high-precision categorization and validation of massive email lists. Unlike standard sorters, this ULTRA version incorporates advanced heuristics, machine learning patterns, and real-time DNS validation.

## 🚀 Ultra Version Features (v1.1)

- **MX-Based Provider Identification**: Accurately identifies providers like Google Workspace, Office 365, Yahoo, AOL, and various global providers even when custom domains are used.
- **Fuzzy Matching (Levenshtein)**: Identifies providers even with subtle MX record variations or misconfigurations.
- **Regex Mastery**: Uses intricate regular expression patterns for precise identification of complex mail infrastructures.
- **ML-Lite Classification**: Weight-based heuristic engine to predict provider types for unknown or ambiguous MX records.
- **Real-Time DNS Liveness**: Automatically filters out "Dead Domains" that have no valid A record, saving you time and resources.
- **SQLite Knowledge Base**: Integrated database (`magxxic_knowledge.db`) to cache domain-to-provider mappings and store user overrides.
- **User Feedback Loop**: Right-click any identified email in the GUI to override its provider mapping, which is then learned and applied to all future emails from that domain.
- **High-Performance Asynchronous Processing**: Scalable concurrency (default 50-100) using `asyncio` and `aiodns`.
- **Professional Ultra GUI**: A multi-tab dark-themed interface with real-time statistics, activity logging, and override management.

## Project Structure

- `magxxic_sorter_gui.py`: The main ULTRA GUI application.
- `email_sorter.py`: CLI version of the tool.
- `sorter_utils.py`: Enhanced sorting logic with Fuzzy Match, Regex, and DNS Liveness.
- `ml_lite.py`: The heuristic weight-based prediction engine.
- `db_mgr.py`: SQLite database manager for persistence and feedback.
- `provider_config.py`: Centralized mapping of MX record patterns.
- `activation_mgr.py`: Handles HWID generation and token validation.
- `admin_activation_kit.py`: Admin tool for token generation.

## Activation

The application is hardware-locked to your system.
1.  Launch the application.
2.  Copy your **HWID**.
3.  Provide the HWID to your administrator for an **Activation Token**.
4.  Enter the token to unlock the ULTRA features.

## Requirements

- Python 3.8+
- `aiodns`: Asynchronous DNS queries.
- `pycares`: Dependency of aiodns.
- `sqlite3`: Standard Python library for the database.
- `tkinter`: Standard Python library for GUI.

## Setup Instructions

### 1. Install Dependencies

**For Windows Users:**
Double-click `setup.bat` to automatically install dependencies and launch the ULTRA GUI.

**Manual Installation:**
```bash
pip install aiodns pycares
```

### 2. Usage

#### Using the ULTRA GUI

Run the GUI script:
```bash
python magxxic_sorter_gui.py
```

1.  **Browse** for your `Mail File`.
2.  Select an **Output Dir**.
3.  Click **START** to begin.
4.  Use the **Recent Activity** tab to monitor real-time identifications.
5.  **Feedback**: Right-click a row in Activity to manually override a domain's provider mapping.

#### Using the CLI
```bash
python email_sorter.py
```

## Sorting Categories (80+ Patterns)

The ULTRA version identifies a massive range of providers, including:
- **Global Leaders**: Gmail, Office365, iCloud, Zoho, Protonmail.
- **Regional Giants**: Yandex, Mail.ru, GMX, Mail.com.
- **Chinese Powerhouses**: QQ, Netease (163/126), Aliyun, Sina, 263.
- **Webmail/Hosting**: Zimbra, Roundcube, Horde, Rainloop, cPanel, Plesk.
- **Security & Filters**: Mimecast, Proofpoint, Barracuda, MessageLabs.
- **Dead Domains**: Automatically identifies domains that are no longer active.

## License

This project is for educational and professional use. Ensure compliance with all regional regulations regarding email processing.
