import requests
import json
import os
from datetime import datetime, timedelta

# Constants
API_KEY = ""
BASE_URL = "https://api.sam.gov/opportunities/v2/search"
LIMIT = 1000
PTYPE = "o,r,p,i,k"
STATUS = "active"
OFFSET = 200
BASE_DIRECTORY = "sam_gov_files"
OUTPUT_FILE = "updated_response.json"


os.makedirs(BASE_DIRECTORY, exist_ok=True)


posted_to = datetime.now()
posted_from = posted_to - timedelta(days=1)
posted_from_str = posted_from.strftime("%m/%d/%Y")
posted_to_str = posted_to.strftime("%m/%d/%Y")

#request to the API
params = {
    "api_key": API_KEY,
    "postedFrom": posted_from_str,
    "postedTo": posted_to_str,
    "limit": LIMIT,
    "ptype": PTYPE,
    "status": STATUS,
    "offset": OFFSET
}

print("Sending request to SAM.gov API...")
response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    print("Request successful! Processing response...")
    data = response.json()
else:
    print(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
    exit(1)


valid_set_asides = {"SBA", "SBP", "WOSB", "WOSBSS", "EDWOSB", "EDWOSBSS"}


filtered_by_set_aside = [
    record for record in data.get('opportunitiesData', [])
    if record.get('typeOfSetAside') in valid_set_asides
]

print(f"Filtered {len(filtered_by_set_aside)} records based on typeOfSetAside.")


exclusion_keywords = [
     "service", "services", "replacement", "install", "operations", "portable", "test", "editing", "supervision", 
    "meats", "meals", "meal", "rental", "assistant", "recycling", "recycle", "renovation", "renovate", "vehicle", 
    "assessment", "upfitting", "stabilization", "delivery", "food", "materials", "replace", "contract", "foods", 
    "upgrade", "transport", "reforestation", "project", "relocation", "inspection", "repair", "maintenance", "support",
    "evaluation", "consulting", "subscription", "planning", "cleaning", "janitorial", "lodging", "facilities", "pumping",
    "event", "pest", "base", "tree", "improvement", "rebuilding", "rehabilitation", "reconstruction", "housing",
    "facility", "building", "shed", "roofing", "flooring", "insulation", "modification", "landscaping", "fence",
    "alarm", "dredging", "sewer", "staffing", "solicitation", "proposal", "procurement", "investments", "security",
    "surveillance", "outsourcing", "software", "license", "cybersecurity", "network", "analytics", "cloud",
    "database", "digital", "clerk", "education", "training", "curriculum", "workforce", "technical", "study", "analysis",
    "research", "feasibility", "pilot", "resource", "structural", "botany", "conference", "venue", "temporary",
    "toilets", "handwashing", "court", "governance", "auditing", "compliance", "administration", "task", "drawing", 
    "drawings", "re-finishing", "physician", "medicine", "removal", "restoration", "restore", "remove", "treat", 
    "treatment", "lift", "lifts", "cutter", "national", "park", "purchase", "soil", "field", "nursery", "fy"
]


def contains_exclusion_keyword(title):
    return any(keyword.lower() in title.lower() for keyword in exclusion_keywords)


filtered_by_title = [
    record for record in filtered_by_set_aside
    if not contains_exclusion_keyword(record.get('title', ''))
]

print(f"Filtered {len(filtered_by_title)} records after title filtering.")


filtered_by_active = [
    record for record in filtered_by_title
    if record.get('active') == "Yes"
]

print(f"Filtered {len(filtered_by_active)} records with active status.")

filtered_final = [
    record for record in filtered_by_active
    if not record.get('solicitationNumber', '').startswith("SP")
]

print(f"Filtered {len(filtered_final)} records after removing solicitationNumbers starting with 'SP'.")

# Download resource links and update JSON with local paths
for opportunity in filtered_final:
    solicitation_id = opportunity.get("solicitationNumber", "unknown")
    notice_id = opportunity.get("noticeId", "unknown")

    
    solicitation_directory = os.path.join(BASE_DIRECTORY, solicitation_id)
    os.makedirs(solicitation_directory, exist_ok=True)

   
    resource_links = opportunity.get("resourceLinks")
    if not isinstance(resource_links, list): 
        resource_links = []

    local_files = []
    for index, link in enumerate(resource_links):
        file_extension = link.split("/")[-1].split(".")[-1]  
        file_name = f"{notice_id}_{index}.{file_extension}" if "." in file_extension else f"{notice_id}_{index}.pdf"
        file_path = os.path.join(solicitation_directory, file_name)

        try:
            file_response = requests.get(link, stream=True)
            if file_response.status_code == 200:
                with open(file_path, "wb") as output_file:
                    for chunk in file_response.iter_content(chunk_size=1024):
                        output_file.write(chunk)
                local_files.append(file_path)
                print(f"Downloaded: {file_path}")
            else:
                print(f"Failed to download: {link} (Status Code: {file_response.status_code})")
        except Exception as e:
            print(f"Error downloading {link}: {e}")

   
    opportunity["localResourceLinks"] = local_files


output_path = os.path.join(BASE_DIRECTORY, OUTPUT_FILE)
with open(output_path, "w") as updated_file:
    json.dump(filtered_final, updated_file, indent=4)

print(f"Updated JSON saved at: {output_path}")
