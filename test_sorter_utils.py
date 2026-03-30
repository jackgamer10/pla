import asyncio
import aiodns
from sorter_utils import identify_provider, levenshtein_distance, fuzzy_match_provider

def test_fuzzy():
    print("Testing Levenshtein Distance...")
    assert levenshtein_distance("gmail", "gmai") == 1
    assert levenshtein_distance("gmail", "gmall") == 1
    print("Levenshtein Distance OK.")

    print("Testing Fuzzy Match Provider...")
    # 'google.com' is in mapping for Gmail. Let's see if 'google.co' matches.
    # Note: MX_PROVIDER_MAPPING['google.com'] = 'Gmail'
    match = fuzzy_match_provider("alt1.aspmx.google.co")
    print(f"Fuzzy Match for google.co: {match}")

    print("Testing Heuristic identification...")
    res = identify_provider([], "webmail.example.com")
    assert res == "Webmail(Generic)"
    print("Heuristic identification OK.")

if __name__ == "__main__":
    test_fuzzy()
