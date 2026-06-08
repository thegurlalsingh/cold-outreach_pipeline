import os
import sys
import json
import time
from dotenv import load_dotenv

load_dotenv()

OCEAN_API_KEY    = os.getenv("OCEAN_API_KEY")
PROSPEO_API_KEY  = os.getenv("PROSPEO_API_KEY")
BREVO_API_KEY    = os.getenv("BREVO_API_KEY")
SENDER_EMAIL     = os.getenv("SENDER_EMAIL")
SENDER_NAME      = os.getenv("SENDER_NAME")

from stages.ocean import find_similar_companies
from stages.prospeo import search_people, search_emails
from stages.brevo import send_email, build_subject, build_html_body


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <seed_domain>")
        sys.exit(1)

    seed_domain = sys.argv[1]

    print()
    print("ASSIGNMENT - COLD OUTREACH PIPELINE — STARTING")
    print()
    print(f"Seed domain : {seed_domain}")
    print()

    print("Finding lookalike companies via Ocean.io...")
    print()

    try:
        domains = find_similar_companies(seed_domain, OCEAN_API_KEY)
    except Exception as e:
        print(f"Stage 1 failed: {e}")
        sys.exit(1)

    if not domains:
        print("No lookalike companies found. Exiting.")
        sys.exit(0)

    print(f"Found {len(domains)} lookalike domains:")
    for d in domains:
        print(f"1. {d}")

    with open("ocean_stage1_output.json", "w") as f:
        json.dump(domains, f, indent=4)
    print(f"  Saved → ocean_stage1_output.json")
    print()

    print("Finding people via Prospeo...")
    print()

    stage2_results = []
    for domain in domains:
        contacts = search_people(domain, PROSPEO_API_KEY)[:2]
        stage2_results.append({"domain": domain, "contacts": contacts})
        print(f"{domain} → {len(contacts)} contacts found")
        time.sleep(3)

    total_contacts = sum(len(c["contacts"]) for c in stage2_results)
    print(f"Total people found: {total_contacts}")

    with open("prospeo_stage2_output.json", "w") as f:
        json.dump(stage2_results, f, indent=4)
    print(f"Saved → prospeo_stage2_output.json")
    print()

    if total_contacts == 0:
        print("No people found. Exiting.")
        sys.exit(0)


    print("Finding emails via Prospeo...")
    print()

    enriched_contacts = []
    for company in stage2_results:
        for contact in company.get("contacts", []):
            linkedin_url = contact.get("linkedin_url")

            if not linkedin_url:
                print(f"Skipping {contact.get('full_name')} — no LinkedIn URL")
                continue

            email = search_emails(linkedin_url, PROSPEO_API_KEY)

            if email:
                contact["email"] = email
                enriched_contacts.append(contact)
                print(f"{contact.get('full_name')} → {email}")
            else:
                print(f"{contact.get('full_name')} — email not found")

            time.sleep(3)

    print(f"Resolved {len(enriched_contacts)} emails")

    with open("prospeo_stage3_output.json", "w") as f:
        json.dump(enriched_contacts, f, indent=4)
    print(f"Saved → prospeo_stage3_output.json")
    print()

    if not enriched_contacts:
        print("No verified emails found. Exiting.")
        sys.exit(0)

    print()
    # print("CHECKPOINT — REVIEW BEFORE SENDING")
    # print()
    # print(f"Ready to email   : {len(enriched_contacts)} contacts")
    # print(f"Sending from     : {SENDER_NAME} | {SENDER_EMAIL}")
    # print()

    # sample = enriched_contacts[0]
    # print("  Preview of first email:")
    # print()
    # print(f"To : {sample.get('full_name')} | {sample.get('email')}")
    # print(f"Title : {sample.get('current_job_title')}")
    # print(f"Subject : {build_subject(sample)}")
    # print()
    # print()

    # confirm = input("  Send emails to all contacts above? [yes/no]: ").strip().lower()
    # if confirm not in ("yes", "y"):
    #     print("\n  Aborted. No emails sent.")
    #     sys.exit(0)

    # print()
    print("Sending outreach emails via Brevo...")
    print()

    sent = 0
    failed = 0

    for contact in enriched_contacts:
        success = send_email(contact, BREVO_API_KEY, SENDER_EMAIL, SENDER_NAME)
        if success:
            sent += 1
        else:
            failed += 1
        time.sleep(3)

    print()
    print()
    print("PIPELINE COMPLETE")
    print()
    print(f"Lookalike domains : {len(domains)}")
    print(f"People found : {total_contacts}")
    print(f"Emails resolved : {len(enriched_contacts)}")
    print(f"Emails sent : {sent}")
    print(f"Emails failed : {failed}")
    print()


if __name__ == "__main__":
    main()
