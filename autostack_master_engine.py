import os
import requests
import json
from datetime import datetime

# Environment Variables
GUMROAD_TOKEN = os.environ.get("GUMROAD_ACCESS_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

GUMROAD_API_BASE = "https://api.gumroad.com/v2"

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini API Error: {e}")
    return "Error generating content via AI."

def fetch_gumroad_sales():
    if not GUMROAD_TOKEN:
        print("No Gumroad token found. Skipping sales sync.")
        return []
    url = f"{GUMROAD_API_BASE}/sales"
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("sales", [])
    except Exception as e:
        print(f"Gumroad API Error: {e}")
    return []

def create_ai_digital_product():
    if not GUMROAD_TOKEN or not GEMINI_KEY:
        print("Missing API keys for product creation.")
        return
    
    # Prompt Gemini to invent a profitable digital product
    idea_prompt = "Invent a trending digital product idea (e.g., Notion template, AI prompt bundle, developer boilerplate). Return ONLY a JSON object with keys: 'name', 'description', and 'price_in_cents' (integer between 900 and 2900)."
    ai_response = call_gemini(idea_prompt)
    
    try:
        # Clean response and parse JSON
        cleaned_json = ai_response.replace("```json", "").replace("```", "").strip()
        product_data = json.loads(cleaned_json)
        
        name = product_data.get("name", "AI Productivity Kit")
        description = product_data.get("description", "High-value digital asset for professionals.")
        price = int(product_data.get("price_in_cents", 1900))
        
        url = f"{GUMROAD_API_BASE}/products"
        headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
        payload = {
            "name": name,
            "description": description,
            "price": price,
            "url": name.lower().replace(" ", "-").replace(":", "")
        }
        
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 201 or response.status_code == 200:
            print(f"Successfully created new product: {name}")
        else:
            print(f"Failed to create product on Gumroad: {response.text}")
    except Exception as e:
        print(f"Product Generation Parse Error: {e}")

def update_financial_ledger(sales):
    total_revenue = sum([float(sale.get("price", 0)) / 100 for sale in sales])
    total_sales_count = len(sales)
    
    ledger_content = f"""# Autostack Financial Ledger
*Last Updated:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

## Summary Metrics
* **Total Revenue:** ${total_revenue:.2f}
* **Total Sales Count:** {total_sales_count}

## Recent Transactions
| Date | Product | Amount | Customer Email |
| :--- | :--- | :--- | :--- |
"""
    for sale in sales[:20]:
        date = sale.get("created_at", "N/A")
        product = sale.get("product_name", "Digital Asset")
        amount = f"${float(sale.get('price', 0)) / 100:.2f}"
        email = sale.get("email", "Anonymous")
        ledger_content += f"| {date} | {product} | {amount} | {email} |\n"

    with open("FINANCIAL_LEDGER.md", "w") as f:
        f.write(ledger_content)
    print("FINANCIAL_LEDGER.md updated successfully.")

def generate_marketing_content():
    prompt = "Generate 3 high-converting social media promotional posts (Twitter/X and LinkedIn style) for trending digital products and assets on an online digital storefront. Include catchy hooks, value propositions, and a placeholder link."
    ai_copy = call_gemini(prompt)

    promo_content = f"""# Daily Marketing Promos
*Generated:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

{ai_copy}
"""
    with open("DAILY_MARKETING_PROMOS.md", "w") as f:
        f.write(promo_content)
    print("DAILY_MARKETING_PROMOS.md updated successfully.")

if __name__ == "__main__":
    print("Initializing Autostack Master Engine...")
    create_ai_digital_product()
    sales_data = fetch_gumroad_sales()
    update_financial_ledger(sales_data)
    generate_marketing_content()
    print("Autostack execution cycle completed successfully.")
