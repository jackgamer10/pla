import asyncio
import aiodns
import re
from provider_config import MX_PROVIDER_MAPPING

async def get_mx_record(domain, resolver):
    """Asynchronously fetches the MX record for a given domain."""
    try:
        # result = await resolver.query_dns(domain, 'MX') # aiodns >= 3.0.0
        # For compatibility with older aiodns if necessary, but query() is deprecated
        result = await resolver.query(domain, 'MX')
        mx_records = [str(rdata.host).lower() for rdata in result]
        return mx_records
    except aiodns.error.DNSError:
        return None
    except Exception:
        return None

def identify_provider(mx_records):
    """Identifies the email provider based on MX record patterns."""
    if not mx_records:
        return 'Others(No_MX)'

    for mx in mx_records:
        for pattern, provider in MX_PROVIDER_MAPPING.items():
            if pattern in mx:
                return provider

    return 'Others(MX)'

async def process_email_base(email, resolver):
    """Core logic to identify a provider for a single email."""
    match = re.search(r'@([\w\.-]+)', email)
    if not match:
        return 'Unknown'

    domain = match.group(1).lower()
    mx_records = await get_mx_record(domain, resolver)
    return identify_provider(mx_records)
