import sys
import os
import json
import time
import requests

def build_subject(contact: dict) -> str:
    first_name = contact.get("full_name")
    company = contact.get("company_name")
    return f"Subject - {first_name}"

def build_html_body(contact: dict) -> str:
    first_name = contact.get("full_name")
    company = contact.get("company_name")
    title = contact.get("current_job_title")

    title_line = f"Given your work as {title}"

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 15px; color: #222; line-height: 1.7;">
    <p>Hi {first_name},</p>
    <p>{title_line}, I thought you would be worth reaching out directly.</p>

    <p>We help B2B SaaS companies scale their user acquisition. I’d love to share a few ideas on how you could amplify your lead flow.</p>
    <p>Are you open to a brief call next week?</p>
    <p>Thanks,</p>
    <p>Gurlal Singh</p>
    </body>
    </html>
    """

def send_email(contact: dict, api_key: str, sender_email: str, sender_name: str) -> bool:
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    receiver_email = contact.get("email")
    receiver_name = contact.get("full_name")

    if not receiver_email or "-" in receiver_email:
        print(f"Skipping contact {contact.get("full_name")} with invalid email: {receiver_email}")
        return False
    
    if not receiver_name:
        print(f"Contact {contact.get("email")} has no name, skipping...")
        return False
    
    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": receiver_email,
                "name": receiver_name
            }
        ],
        "subject": build_subject(contact),
        "htmlContent": build_html_body(contact)
    }

    try: 
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 429:
            print("Rate Limited. Please wait for 60 seconds")
            time.sleep(60)
            response = requests.post(url, headers=headers, json=payload)
            
        if response.status_code in (200, 201):
            data = response.json()
            message_id = data.get("messageId")
            print(f"Email sent successfully to {receiver_email} with message ID: {message_id}")
            return True
        else:
            print(f"Error sending email to {receiver_email}: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {str(e)}")
        return False
        

def main():
    if len(sys.argv) < 2:
        print("Write all arguments carefully!!!!")
        sys.exit(1)

    input_file = sys.argv[1]
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv("SENDER_NAME")

    try:
        with open(input_file, "r") as f:
            inputs = json.load(f)

    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        sys.exit(1)

    if not inputs:
        print("No contacts found in the input file")
        sys.exit(0)

    print(f"Total contacts to mail: {len(inputs)}")
    print(f"Sending from {sender_name} <{sender_email}>")
    print("Preview of first email: ")
    if inputs:
        sample = inputs[0]
        print(f"To: {sample.get("full_name")} - {sample.get("email")}")
        print(f"Title: {sample.get("current_job_title")}")
        print(f"Subject: {build_subject(sample)}")
        print(f"Body: {build_html_body(sample)}")

        print()
        confirm = input("Confirm: Send emails to all contacts with above content? [yes/no]:").strip().lower()

        if confirm not in ("yes", "y"):
            print("Exiting")
            sys.exit(0)

        print("Sending emails....")
        sent = 0
        failed = 0

        for contact in inputs:
            success = send_email(contact, api_key, sender_email, sender_name)
            if success:
                sent += 1
            else:
                failed += 1

            time.sleep(3)
            print(f"Email sent to {contact.get("email")} | Success: {sent} | Failed: {failed}")

        print("Done!")
        print(f"Total sent: {sent}")
        print(f"Total failed: {failed}")

if __name__ == "__main__":
    main()
    
    

    
    
        