import os
import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Initialize OpenAI client
import os

client = OpenAI(api_key="")

# Retry logic for robustness
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def chat_completion_request(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Error: {e}")
        return None

# Load filtered opportunities
input_path = os.path.join("sam_gov_files", "updated_response.json")
with open(input_path, "r") as file:
    data = json.load(file)

# System and instruction prompts
system_prompt = {
    "role": "system",
    "content": (
        "You are a pricing analyst for government contracts. "
        "Your task is to estimate a price range in USD for each solicitation based on the provided text. "
        "Use historical contract knowledge, typical pricing ranges, and context clues. "
        "If specific quantities, product types, or scopes are missing, give your best estimate based on similar contracts. "
        "Always provide a price range in the format '$1,000 - $5,000'. "
        "Never use vague terms like 'around', 'approximately', or 'depends'. "
        "Only output the price range and nothing else."
    )
}

# Prepare output
results = []

for item in data:
    solicitation_number = item.get("solicitationNumber", "")
    title = item.get("title", "")
    description = item.get("description", "")

    # Combine title and description as the text prompt
    text = f"Title: {title}\nDescription: {description}"

    if not text.strip():
        results.append({
            "solicitationNumber": solicitation_number,
            "estimatedPrice": ""
        })
        continue

    user_prompt = {
        "role": "user",
        "content": (
            f"Estimate the expected price range (in USD) for the following government contract solicitation.\n"
            f"Provide a specific price range like '$5,000 - $10,000'.\n"
            f"Only output the price range.\n"
            f"Text: {text}"
        )
    }

    response = chat_completion_request([system_prompt, user_prompt])

    if response and response.choices:
        reply = response.choices[0].message.content.strip()
    else:
        reply = ""

    results.append({
        "solicitationNumber": solicitation_number,
        "estimatedPrice": reply
    })

# Save to output file
output_path = os.path.join("sam_gov_files", "estimated_prices.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=4)

print(f"Price estimation complete. Results saved to: {output_path}")

   
