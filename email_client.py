# email_client.py

from imapclient import IMAPClient
import pyzmail
import auth
import logging


def connect_to_email():
    logging.info("Establishing connection to IMAP server...")
    client = IMAPClient(auth.IMAP_HOST, ssl=True)
    client.login(auth.EMAIL_ACCOUNT, auth.APP_PASSWORD)
    logging.info("IMAP connection established.")
    return client


def search_emails_by_criteria(client, sender, title_keyword, body_keyword):
    logging.info(f"Searching emails with criteria - Sender: {sender}, Title: {title_keyword}, Body contains: {body_keyword}")
    client.select_folder('INBOX', readonly=True)
    criteria = [
        'FROM', sender,
        'SUBJECT', title_keyword,
        'TEXT', body_keyword
    ]
    messages = client.search(criteria)
    logging.info(f"Emails found: {len(messages)}")
    return messages


def fetch_email_body(client, uid):
    logging.info(f"Fetching email UID: {uid}")
    message_data = client.fetch(uid, ['BODY[]'])
    raw_email = message_data[uid][b'BODY[]']
    email_message = pyzmail.PyzMessage.factory(raw_email)

    email_body = None
    if email_message.text_part:
        email_body = email_message.text_part.get_payload().decode(email_message.text_part.charset or 'utf-8', errors='replace')
        logging.info(f"Retrieved plain text email body for UID: {uid}")
    elif email_message.html_part:
        email_body = email_message.html_part.get_payload().decode(email_message.html_part.charset or 'utf-8', errors='replace')
        logging.info(f"Retrieved HTML email body for UID: {uid}")
    else:
        logging.warning(f"No email body found for UID: {uid}")

    subject = email_message.get_subject()
    logging.info(f"Email subject for UID {uid}: {subject}")

    return subject, email_body
