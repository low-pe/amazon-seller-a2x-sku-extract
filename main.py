# main.py

import csv
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from email_client import connect_to_email, search_emails_by_criteria, fetch_email_body
from openai_client import extract_sku_name
from tqdm import tqdm
from multiprocessing import Value

csv_results_file = 'sku_results.csv'
csv_lock = Lock()

DISCORD_WEBHOOK_URL = "WEBHOOKURLHERE"

def load_existing_skus(csv_file):
    if not os.path.exists(csv_file):
        return set()
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return {row['SKU'] for row in reader}

def append_result_to_csv(result):
    with csv_lock:
        file_exists = os.path.isfile(csv_results_file)
        mode = 'a' if file_exists else 'w'
        with open(csv_results_file, mode=mode, newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['SKU', 'Item Name', 'Email Subject', 'Criteria Used'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)

def process_sku_batch(sku_list, matched_counter, pbar, max_retries=3):
    criteria_list = [
        {"sender": "donotreply@amazon.com", "title_keyword": "Refund Initiated for Order", "description": "Refund Initiated"},
        {"sender": "seller-notification@amazon.com", "title_keyword": "Sold, ship now", "description": "Sold Ship Now"},
        {"sender": "seller-notification@amazon.com", "title_keyword": "Amazon Listing Created -", "description": "Listing Created"}
    ]

    client = None
    for attempt in range(max_retries):
        try:
            client = connect_to_email()
            client.select_folder('INBOX', readonly=True)
            break
        except Exception as e:
            tqdm.write(f"IMAP connection attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    else:
        tqdm.write("IMAP connection failed after maximum retries.")
        return

    try:
        for sku in sku_list:
            found = False
            for criteria in criteria_list:
                sender = criteria['sender']
                title_keyword = criteria['title_keyword']
                criteria_desc = criteria['description']

                messages = search_emails_by_criteria(client, sender, title_keyword, sku)
                tqdm.write(f"[{criteria_desc}] Emails found for SKU '{sku}': {len(messages)}")

                for uid in messages:
                    subject, email_body = fetch_email_body(client, uid)
                    if email_body:
                        sku_name = extract_sku_name(sku, email_body, criteria_desc)

                        # Explicitly ensure extracted SKU name isn't empty or invalid
                        if sku_name.strip():
                            result = {
                                'SKU': sku,
                                'Item Name': sku_name,
                                'Email Subject': subject,
                                'Criteria Used': criteria_desc
                            }
                            append_result_to_csv(result)

                            with matched_counter.get_lock():
                                matched_counter.value += 1

                            tqdm.write(f"✅ [{criteria_desc}] SKU '{sku}' matched successfully: {sku_name}")

                            found = True
                            break

                if found:
                    break

                time.sleep(0.5)

            if not found:
                tqdm.write(f"⚠️ No match found for SKU '{sku}'. Not logging to CSV.")

            pbar.update(1)

    finally:
        if client:
            client.logout()
        time.sleep(1)

def chunk_skus(sku_list, n_chunks):
    avg = len(sku_list) / float(n_chunks)
    chunks = []
    last = 0.0
    while last < len(sku_list):
        chunks.append(sku_list[int(last):int(last + avg)])
        last += avg
    return chunks

def send_discord_notification(matched_count):
    message = {
        "content": f"✅ **SKU Processing Complete:** {matched_count} new SKUs matched successfully."
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=message)
        tqdm.write("✅ Discord notification sent.")
    except Exception as e:
        tqdm.write(f"⚠️ Failed to send Discord notification: {e}")

def main():
    sku_file = input("Enter the path to your SKU file (one SKU per line): ").strip()

    try:
        with open(sku_file, 'r', encoding='utf-8') as file:
            SKU_LIST = [line.strip() for line in file if line.strip()]
        tqdm.write(f"Total SKUs loaded: {len(SKU_LIST)}")
    except Exception as e:
        tqdm.write(f"⚠️ Error loading SKU file '{sku_file}': {e}")
        return

    existing_skus = load_existing_skus(csv_results_file)
    new_skus = [sku for sku in SKU_LIST if sku not in existing_skus]

    if not new_skus:
        tqdm.write("No new SKUs to process. Exiting.")
        return

    max_threads = 5
    sku_batches = chunk_skus(new_skus, max_threads)
    matched_counter = Value('i', 0)

    total_skus = len(new_skus)
    pbar = tqdm(total=total_skus, desc='Processing SKUs', unit='sku', ncols=100, position=0, leave=True)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(process_sku_batch, batch, matched_counter, pbar) for batch in sku_batches]

        for future in as_completed(futures):
            future.result()

    pbar.close()

    tqdm.write(f"🏁 All SKUs processed. Total matched: {matched_counter.value}")

    send_discord_notification(matched_counter.value)

if __name__ == "__main__":
    main()
