# 🧠 Web-Scraped Price Estimation using NLP and LLMs

This project is an end-to-end pipeline that combines **web scraping**, **Natural Language Processing (NLP)**, and **Generative AI** (LLMs like GPT-4 and GPT-3.5) to estimate pricing information from free-form solicitation text. It is designed to transform unstructured procurement listings into structured, AI-driven price predictions.

---

## 🔧 Key Features

- 🌐 **Web Scraping from SAM.gov** via API  
- 📄 **Title & Description Filtering** to retain only relevant product-based opportunities  
- 📥 **Automated Document Downloading** for deeper context  
- 🧠 **LLM-Powered NLP Pipeline** for semantic understanding and price inference  
- 🔁 **Batch & Retry Support** for robustness  
- 📊 **Structured JSON Outputs** for analysis or integration into BI systems  

---

## 🧠 Technologies Used

| Category         | Tools/Libraries                                |
|------------------|-------------------------------------------------|
| Web Scraping     | `requests`, `json`, `SAM.gov API`              |
| LLM Integration  | `OpenAI GPT-4`, `GPT-3.5-turbo`                 |
| NLP Techniques   | Prompt Engineering, Contextual Understanding   |
| File Handling    | `os`, `datetime`, `file streams`               |
| Error Handling   | `tenacity` for retries                         |
| Output Formats   | `JSON` (intermediate and final results)        |

---


---

## 🛠️ Project Components (Script Breakdown)

### 1. `solicitation_downloader.py`  
**Purpose:**  
Fetches active solicitations from SAM.gov using their API and filters them using predefined criteria.

**Key Actions:**
- Applies filters for **set-aside types** (e.g., WOSB, SBA).
- Removes records with **irrelevant keywords** (like "maintenance", "consulting").
- Downloads linked **PDFs/documents** and stores them in folders named by solicitation number.
- Saves the cleaned and enriched data to `updated_response.json`.

---

### 2. `open_api test.py`  
**Purpose:**  
Uses **GPT-4** to estimate a **price range** for each solicitation individually using prompt engineering.

**Key Features:**
- Uses `tenacity` to retry failed API calls.
- Crafts structured prompts using solicitation title and description.
- Sends these to OpenAI with a system role that instructs the model to output strict price ranges (e.g., "$5,000 - $10,000").
- Outputs results to `estimated_prices.json`.

---

### 3. `openai api.py`  
**Purpose:**  
Uses **GPT-3.5-turbo** to estimate prices in **batch mode**, making it more cost-efficient and faster for large datasets.

**Key Features:**
- Batches 10 solicitations per call to reduce token cost.
- Uses a single GPT call to classify whether a solicitation is a **product or service** and extract price only for product listings.
- Outputs all results to the same `estimated_prices.json` file.

---

## 🧪 Prompt Engineering Examples

**System Prompt (GPT-4):**
> You are a pricing analyst. Estimate a price range in USD based on the solicitation text. Output only the range (e.g., "$1,000 - $5,000").




