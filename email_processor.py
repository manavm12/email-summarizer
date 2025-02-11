import os
import email
import re
from bs4 import BeautifulSoup

def extract_email_content(raw_email):
    """Extracts sender, subject, and clean text body from an email."""
    
    msg = email.message_from_string(raw_email)
    sender = msg["From"]
    subject = msg["Subject"]

    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
            elif content_type == "text/html" and body is None:
                html_body = part.get_payload(decode=True).decode(errors="ignore")
                body = clean_html(html_body)
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    body = clean_email_text(body)

    return {"sender": sender, "subject": subject, "body": body}

def clean_html(html_content):
    """Converts HTML to plain text using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

def clean_email_text(text):
    """Cleans email text by removing extra spaces, signatures, and footers."""
    text = re.sub(r'\n+', '\n', text)  
    text = re.sub(r'(--|__|Thanks,|Best,|Regards,).*$', '', text, flags=re.DOTALL)  
    return text.strip()

def process_eml_file(file_path):
    """Reads a .eml file and extracts its content."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_email = f.read()
    
    email_data = extract_email_content(raw_email)
    return email_data

def process_emails_in_folder(folder_path):
    """Processes all .eml files in a folder."""
    email_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".eml"):
            file_path = os.path.join(folder_path, filename)
            email_data = process_eml_file(file_path)
            email_list.append(email_data)

    return email_list

if __name__ == "__main__":
    folder_path = "emails"  # Folder where .eml files are stored
    emails_data = process_emails_in_folder(folder_path)
    
    for email in emails_data:
        print(email)
