import sys
import os
import json
import time
import requests


def search_people(domain_from_ocean: str, api_key: str) -> list[dict]:
    url = "https://api.prospeo.io/search-person"

    required_headers = {
        "Content-Type": "application/json",
        "X-KEY": api_key
    }

    payload = {
        "page": 1,
        "filters": {
            "company": {
                "websites": {
                    "include": [domain_from_ocean]
                },
                "person_seniority": {
                    "include": [
                        "CEO",
                        "Founder/Owner",
                        "Director",
                        "Vice President",
                        "C-Suite"
                    ]
                }
            }
        }
    }

    print(f"Searching people for domain: {domain_from_ocean}...")

    try:
        response = requests.post(
            url,
            headers=required_headers,
            json=payload
        )

        if response.status_code == 429:
            print("Rate Limited. Please wait for 60 seconds")
            time.sleep(60)
            response = requests.post(
                url,
                headers=required_headers,
                json=payload
            )

        if response.status_code != 200:
            print(
                f"Error searching domain {domain_from_ocean}: "
                f"{response.status_code} - {response.text}"
            )
            return []

        data = response.json()
        results = data.get("results", [])

        contacts = []

        for result in results:
            person = result.get("person", {})
            company = result.get("company", {})

            if not person:
                continue
                
            # print(f"DEBUG - {person.get("linkedin_url")}")

            contacts.append({
                "person_id": person.get("person_id"),
                "full_name": person.get("full_name"),
                "linkedin_url": person.get("linkedin_url"),
                "current_job_title": person.get("current_job_title"),
                "company_name": company.get("name")
            })

        return contacts

    except Exception as e:
        print(
            f"An error occurred while searching people for "
            f"{domain_from_ocean}: {str(e)}"
        )
        return []


def search_emails(linkedin_url: str, api_key: str) -> str | None:
    url = "https://api.prospeo.io/enrich-person"

    headers = {
        "Content-Type": "application/json",
        "X-KEY": api_key
    }

    payload = {
        "data": {
            "linkedin_url": linkedin_url
        }
    }

    print(f"DEBUG - {payload}")

    print(f"Finding email for linkedin profile: {linkedin_url}...")

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        print(f"DEBUG - {response.text}")

        if response.status_code == 429:
            print("Rate Limited. Please wait for 60 seconds")
            time.sleep(60)
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            print(
                f"Error searching linkedin url {linkedin_url}: "
                f"{response.status_code} - {response.text}"
            )
            return None

        data = response.json()

        if data.get("error") is True:
            print(
                f"Failed to enrich: "
                f"{data.get('message', 'Unknown error')}"
            )
            return None

        person_obj = data.get("person", {})
        email = None

        if isinstance(person_obj, dict):
            email_obj = person_obj.get("email", {})

            if isinstance(email_obj, dict):
                email = email_obj.get("email")

        return email

    except Exception as e:
        print(
            f"Failed to enrich Linkedin profile "
            f"{linkedin_url}: {str(e)}"
        )
        return None


def main():
    if len(sys.argv) < 3:
        print("Write all arguments carefully!!")
        sys.exit(1)

    api_key = os.getenv("PROSPEO_API_KEY")

    if not api_key:
        print("PROSPEO_API_KEY not found")
        sys.exit(1)

    action = sys.argv[1]
    input_file = sys.argv[2]

    try:
        with open(input_file, "r") as f:
            inputs = json.load(f)

    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        sys.exit(1)

    results = []

    if action == "search":

        if not isinstance(inputs, list):
            print("Input is not a list of domains")
            sys.exit(1)

        for domain in inputs:
            contacts = search_people(domain, api_key)

            results.append({
                "domain": domain,
                "contacts": contacts
            })

            time.sleep(3)

        print(
            f"Completed search!! "
            f"Processed {len(results)} domains..."
        )

        output_file = "prospeo_stage2_output.json"

    elif action == "enrich":

        if not isinstance(inputs, list):
            print("Input is not a list of contacts")
            sys.exit(1)

        for company in inputs:
            contacts = company.get("contacts", [])

            for contact in contacts:
                linkedin_url = contact.get("linkedin_url")

                if not linkedin_url:
                    print(
                        f"Skipping contact "
                        f"{contact.get('full_name')} "
                        f"with no linkedin url"
                    )
                    continue

                email = search_emails(
                    linkedin_url,
                    api_key
                )

                if email:
                    contact["email"] = email
                    results.append(contact)

                    print(
                        f"Found email for "
                        f"{contact.get('full_name')}: "
                        f"{email}"
                    )

                else:
                    print(
                        f"Failed to find email for "
                        f"{contact.get('full_name')}"
                    )

                time.sleep(5)

        print(
            f"Completed search!! "
            f"Found {len(results)} emails..."
        )

        output_file = "prospeo_stage3_output.json"

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

    try:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)

        print(f"Results saved to {output_file}")

    except Exception as e:
        print(
            f"Error saving results to output file: "
            f"{str(e)}"
        )


if __name__ == "__main__":
    main()