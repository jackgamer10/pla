import asyncio
import aiodns
import re
import os
from provider_config import MX_PROVIDER_MAPPING

async def get_mx_record(domain, resolver):
    """Asynchronously fetches the MX record for a given domain."""
    try:
        result = await resolver.query(domain, 'MX')
        mx_records = [str(rdata.host).lower() for rdata in result]
        return mx_records
    except aiodns.error.DNSError:
        return None
    except Exception as e:
        print(f"DNS Error for {domain}: {e}")
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

async def process_email(email, resolver, results, lock):
    """Processes a single email and categorizes it."""
    match = re.search(r'@([\w\.-]+)', email)
    if not match:
        async with lock:
            results['Unknown'].append(email)
        return

    domain = match.group(1).lower()
    mx_records = await get_mx_record(domain, resolver)
    provider = identify_provider(mx_records)

    async with lock:
        if provider not in results:
            results[provider] = []
        results[provider].append(email)

async def sort_emails_by_domain_asyncio(email_file, concurrency=100):
    """Sorts emails from a file by identifying their provider via MX records."""
    results = {'Unknown': []}
    resolver = aiodns.DNSResolver()
    lock = asyncio.Lock()

    async def read_emails(email_file):
        tasks = []
        with open(email_file, 'r', errors='ignore') as f:
            for line in f:
                email = line.strip()
                if not email: continue
                task = asyncio.create_task(process_email(email, resolver, results, lock))
                tasks.append(task)
                if len(tasks) >= concurrency:
                    await asyncio.gather(*tasks)
                    tasks = []
        if tasks:
            await asyncio.gather(*tasks)

    await read_emails(email_file)
    return results

def write_sorted_emails(results, output_dir):
    """Writes sorted emails to separate files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for provider, emails in results.items():
        if not emails: continue
        filename = f"{provider.lower()}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            for email in emails:
                f.write(email + '\n')

async def main():
    email_file = 'emails.txt'
    output_dir = 'sorted_output'

    if not os.path.exists(email_file):
        print(f"Error: {email_file} not found.")
        return

    print(f"Sorting emails from {email_file}...")
    sorted_results = await sort_emails_by_domain_asyncio(email_file)
    write_sorted_emails(sorted_results, output_dir)

    print("\nSorting Summary:")
    for provider, emails in sorted_results.items():
        if emails:
            print(f"{provider}: {len(emails)}")
    print(f"\nEmails sorted and saved in '{output_dir}' folder!")

if __name__ == "__main__":
    asyncio.run(main())
