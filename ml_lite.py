import re

# ML-Lite Weight Matrix
PROVIDER_FEATURES = {
    'Gmail': {'keywords': ['google', 'gmail', 'aspmx'], 'weight': 1.0},
    'Office365': {'keywords': ['outlook', 'protection', 'microsoft', 'onmicrosoft'], 'weight': 1.0},
    'Zoho': {'keywords': ['zoho'], 'weight': 1.0},
    'GoDaddy': {'keywords': ['secureserver', 'godaddy'], 'weight': 1.0},
    'Yandex': {'keywords': ['yandex'], 'weight': 1.0},
    'Zimbra': {'keywords': ['zimbra'], 'weight': 1.0},
    'Roundcube': {'keywords': ['roundcube'], 'weight': 1.0},
    'Webmail(cPanel)': {'keywords': ['cpanel'], 'weight': 1.0},
    'Webmail(Plesk)': {'keywords': ['plesk'], 'weight': 1.0},
    'Others(MX)': {'keywords': ['mail', 'mx'], 'weight': 0.1}
}

def predict_provider_lite(mx_records, domain):
    """Predicts a provider using a heuristic weight-based 'ML-lite' approach."""
    if not mx_records:
        return None

    scores = {provider: 0.0 for provider in PROVIDER_FEATURES}

    for mx in mx_records:
        for provider, info in PROVIDER_FEATURES.items():
            for kw in info['keywords']:
                if kw in mx:
                    scores[provider] += info['weight']

    # Bonus for domain match if MX is ambiguous
    for provider, info in PROVIDER_FEATURES.items():
        for kw in info['keywords']:
            if kw in domain:
                scores[provider] += 0.5

    best_match = max(scores, key=scores.get)
    if scores[best_match] >= 0.5:
        return f"{best_match}(ML-Lite)"

    return None
