import pandas as pd
import random
import os
import json
from datetime import datetime, timedelta

def load_config():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def generate_mock_data(output_path):
    config = load_config()
    app_id = config.get("APP_PACKAGE_ID", "com.ril.shein")
    
    # Phrases aligned with taxonomy keywords
    themes = [
        ("Payments & Refunds", [
            "Payment failed and money was deducted. No refund yet. Very bad experience.",
            "I used a coupon but it was not applied. Wallet shows 0 balance.",
            "Charged twice for one order. UPI transaction failed but money gone.",
            "Refund process is very slow. Still waiting for voucher.",
            "Promo code not working. Cash back not received."
        ]),
        ("Delivery & Logistics", [
            "My order is late. Tracking shows out for delivery since 3 days.",
            "Delivery delay is frustrating. Courier not responding.",
            "Shipment tracking is stuck. Not delivered after 10 days.",
            "Courier guy was rude and delivery was very late.",
            "Waiting for shipment. No update on tracking ID."
        ]),
        ("Wrong / Missing Items", [
            "Received wrong item. I ordered a blue dress but got red pants.",
            "Missing items in my package. 2 products are not there.",
            "Exchange is taking forever. Received something else entirely.",
            "Different product delivered. Very poor quality control.",
            "Part of the order is missing. Incomplete shipment."
        ]),
        ("Returns & Customer Support", [
            "Customer support is not helpful. No response to my help request.",
            "Return pickup failed three times. No one came to collect.",
            "Customer care is useless. No help with my return pickup.",
            "Complaint registered but no response from support team.",
            "Need help with returns but customer care is not answering."
        ]),
        ("App Experience & Stability", [
            "App keeps crashing on my Android phone. Very slow and buggy.",
            "Login issues. Can't sign in to my account. App freezes.",
            "The app is very slow on iPhone. Crashing during checkout.",
            "Buggy interface. Search is not working properly.",
            "App freeze while doing payment. Needs optimization."
        ]),
        ("Product Quality & Pricing", [
            "Quality is poor. Fabric is cheap and thin. Not worth the price.",
            "Size chart is wrong. Fit is very bad. Expensive for this quality.",
            "Fabric feels cheap. Size is too small for me. Not worth it.",
            "Price is too high for this fabric quality. Disappointing fit.",
            "Poor stitching and sizing. Price does not match value."
        ])
    ]

    records = []
    start_date = datetime.now() - timedelta(weeks=10)
    
    for i in range(500):
        theme_name, phrases = random.choice(themes)
        review_text = random.choice(phrases)
        
        # Add metadata
        rating = random.randint(1, 4) # Scraper focuses on 1-4
        days_offset = random.randint(0, 10 * 7)
        review_date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d %H:%M:%S")
        
        records.append({
            "review_id": f"gp_mock_{i}",
            "rating": rating,
            "review_text": review_text,
            "date": review_date,
            "app_id": app_id
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated 300 taxonomy-aligned mock reviews at {output_path}")

if __name__ == "__main__":
    generate_mock_data("data/raw/shein_reviews_raw.csv")
