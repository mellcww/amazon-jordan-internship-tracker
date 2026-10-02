import requests
import os

# Grab the webhook URL from environment variables for security
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

def get_amazon_internships():
    # Amazon's frontend uses this JSON API to populate search results
    url = "https://www.amazon.jobs/en/search.json?base_query=intern&loc_query=Jordan"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    jobs = []
    if response.status_code == 200:
        # Extract the jobs array from the JSON response
        for job in response.json().get("jobs", []):
            jobs.append({
                "id": str(job.get("id_icims")),
                "title": job.get("title"),
                "url": "https://www.amazon.jobs" + job.get("job_path"),
            })
    return jobs

def send_alert(job):
    payload = {
        "content": f"🚨 **New Amazon Internship in Jordan!** 🚨\n**Role:** {job['title']}\n**Apply here:** {job['url']}"
    }
    requests.post(DISCORD_WEBHOOK, json=payload)

def main():
    seen_file = "seen_jobs.txt"
    seen_jobs = set()
    
    # Load previously seen jobs so we don't spam your phone
    if os.path.exists(seen_file):
        with open(seen_file, "r") as f:
            seen_jobs = set(f.read().splitlines())

    current_jobs = get_amazon_internships()
    new_jobs_found = False
    
    # Open the file in append mode to log new jobs
    with open(seen_file, "a") as f:
        for job in current_jobs:
            if job["id"] not in seen_jobs:
                send_alert(job)
                f.write(job["id"] + "\n")
                new_jobs_found = True
                
    if not new_jobs_found:
        print("No new internships found.")

if __name__ == "__main__":
    if DISCORD_WEBHOOK:
        main()
    else:
        print("Error: DISCORD_WEBHOOK environment variable not set.")