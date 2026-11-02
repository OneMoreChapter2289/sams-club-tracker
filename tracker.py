import os
import requests

# 1. ADD ALL YOUR ITEM IDS HERE IN A LIST (SEPARATED BY COMMAS)
ITEM_IDS = ["20970021268", "20954959021", "21070812284", "20970071107", "21068272365"]

# Setup URLs
SAMS_API_URL = f"https://samsclub.com"
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Request headers to look like a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# The background layout query template
def get_graphql_query(item_id):
    return {
        "query": """
        query getProductInventory($itemId: String!) {
            product(id: $itemId) {
                name
                skus {
                    id
                    onlineAvailability {
                        status
                    }
                }
            }
        }
        """,
        "variables": {"itemId": item_id}
    }

def check_all_inventory():
    print(f"Starting inventory check for {len(ITEM_IDS)} items...")
    
    for item_id in ITEM_IDS:
        try:
            query = get_graphql_query(item_id)
            response = requests.post(SAMS_API_URL, json=query, headers=HEADERS, timeout=10)
            data = response.json()
            
            # Extract item details from response
            product_name = data['data']['product']['name']
            skus = data['data']['product']['skus']
            
            # Track if any variant/sku is available
            is_available = False
            for sku in skus:
                status = sku['onlineAvailability']['status']
                if status == "AVAILABLE":
                    is_available = True
                    break # Stop looking at other variations if one is available
            
            if is_available:
                message = f"🚨 **IN STOCK!** 🚨\n**Item:** {product_name}\n**Status:** Currently available online!\n👉 Link: https://samsclub.com{item_id}"
                requests.post(DISCORD_URL, json={"content": message})
                print(f"[{item_id}] {product_name} is IN STOCK! Sent alert.")
            else:
                print(f"[{item_id}] {product_name} is currently out of stock.")
                
        except Exception as e:
            print(f"Error checking item ID {item_id}: {e}")

if __name__ == "__main__":
    check_all_inventory()
