import asyncio
import aiodns
import re
from provider_config import MX_PROVIDER_MAPPING
import db_mgr
from ml_lite import predict_provider_lite

# --- REGEX MASTERY ---
PROVIDER_REGEXES = {
    r"google\.com$": "Gmail",
    r"outlook\.com$": "Office365",
    r"googlemail\.com$": "Gmail",
    r"secureserver\.net$": "GoDaddy",
    r"protection\.outlook\.com$": "Office365",
    r"mail\.protection\.outlook\.com$": "Office365",
    r"mx[0-9]*\.zoho\.com$": "Zoho",
    r"m[0-9]*\.yandex\.ru$": "Yandex",
    r"mail\.ru$": "Mail.ru",
    r"pro\.mail\.ru$": "Mail.ru",
    r"sina\.com$": "Sina",
    r"163\.com$": "Netease(163)",
    r"qq\.com$": "QQMail",
    r"icloud\.com$": "Apple iCloud",
    r"zimbra": "Zimbra",
    r"roundcube": "Roundcube",
    r"cpanel": "Webmail(cPanel)",
    r"plesk": "Webmail(Plesk)",
    r"horde": "Webmail(Horde)",
    r"rainloop": "Webmail(RainLoop)"
}

def levenshtein_distance(s1, s2):
    """Simple pure Python Levenshtein distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def fuzzy_match_provider(mx_host):
    """Checks if mx_host is 'close enough' to known provider patterns."""
    for pattern in MX_PROVIDER_MAPPING.keys():
        dynamic_threshold = max(2, len(pattern) // 4)
        if len(mx_host) >= len(pattern):
            for i in range(len(mx_host) - len(pattern) + 1):
                sub = mx_host[i:i+len(pattern)]
                if levenshtein_distance(sub, pattern) <= dynamic_threshold:
                    return MX_PROVIDER_MAPPING[pattern]
    return None

async def validate_domain_liveness(domain, resolver):
    """Checks if the domain is alive by looking for A record."""
    try:
        await resolver.query(domain, 'A')
        return True
    except aiodns.error.DNSError:
        return False
    except Exception:
        return False

async def get_mx_record(domain, resolver):
    """Asynchronously fetches the MX record for a given domain."""
    try:
        result = await resolver.query(domain, 'MX')
        mx_records = [str(rdata.host).lower().strip('.') for rdata in result]
        return mx_records
    except aiodns.error.DNSError:
        return None
    except Exception:
        return None

def identify_provider(mx_records, domain=None):
    """Identifies the email provider based on MX record patterns, regexes, ML-lite, and heuristics."""
    if not mx_records:
        if domain:
            if any(x in domain for x in ['webmail.', 'cpanel.', 'mail.']):
                return 'Webmail(Generic)'
        return 'Others(No_MX)'

    # 1. Regex Mastery Match
    for mx in mx_records:
        for pattern, provider in PROVIDER_REGEXES.items():
            if re.search(pattern, mx):
                return provider

    # 2. Pattern Match (Substring from Config)
    for mx in mx_records:
        for pattern, provider in MX_PROVIDER_MAPPING.items():
            if pattern in mx:
                return provider

    # 3. ML-Lite Prediction
    prediction = predict_provider_lite(mx_records, domain or "")
    if prediction:
        return prediction

    # 4. Heuristic: Keyword search
    keywords = {
        'secure': 'Webmail(Generic)',
        'cluster': 'Plesk/Generic',
        'spam': 'Others(MX)',
        'filter': 'Others(MX)'
    }
    for mx in mx_records:
        for kw, provider in keywords.items():
            if kw in mx:
                return provider

    # 5. Fuzzy Matching
    for mx in mx_records:
        match = fuzzy_match_provider(mx)
        if match:
            return f"{match}(Fuzzy)"

    return 'Others(MX)'

async def process_email_base(email, resolver):
    """Core logic to identify a provider for a single email with validation."""
    match = re.search(r'@([\w\.-]+)', email)
    if not match:
        return 'Unknown'

    domain = match.group(1).lower()

    # 1. Check Database Cache/Overrides
    cached = db_mgr.get_cached_provider(domain)
    if cached:
        return cached

    # 2. DNS Liveness Check
    is_alive = await validate_domain_liveness(domain, resolver)
    if not is_alive:
        return 'Dead Domain'

    # 3. MX Lookup and identification
    mx_records = await get_mx_record(domain, resolver)
    provider = identify_provider(mx_records, domain)

    # 4. Save to Cache
    if provider not in ['Others(No_MX)', 'Others(MX)', 'Unknown']:
        db_mgr.save_domain_provider(domain, provider)

    return provider
