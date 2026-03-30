import asyncio
import aiodns
import os
import sys
from provider_config import MX_PROVIDER_MAPPING
from sorter_utils import process_email_base
from activation_mgr import get_hwid, is_activated, activate
from branding import print_banner

async def process_email(email, resolver, results, lock):
    """Processes a single email and categorizes it."""
    provider = await process_email_base(email, resolver)

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
    print_banner()
    if not is_activated():
        print("=======================================================")
        print("    MagxxicVOT Advanced Email Sorter - Activation")
        print("=======================================================")
        hwid = get_hwid()
        print(f"\nYour HWID: {hwid}")
        print("Please provide this HWID to get your activation token.")

        token = input("\nEnter Activation Token: ").strip()
        if activate(token):
            print("\n[SUCCESS] Application activated successfully!")
        else:
            print("\n[ERROR] Invalid activation token.")
            sys.exit(1)

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
