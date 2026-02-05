import os
import json
import pandas as pd
from datetime import datetime, timedelta
from google_play_scraper import reviews, Sort

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def run_scraper(app_id=None):
    config = load_config()
    app_id = app_id or config.get("APP_PACKAGE_ID", "com.ril.shein")
    weeks = config.get("DATE_RANGE_WEEKS", 8)
    country = 'in'
    lang = 'en'
    
    # Calculate date cutoff
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    print(f"Scraping {app_id}")
    print(f"Filtering reviews since: {cutoff_date.date()}")
    
    all_captured = []
    
    # Ratings 1 to 4
    for score in [1, 2, 3, 4]:
        print(f"Fetching reviews with rating {score}...")
        result, _ = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=500,
            filter_score_with=score
        )
        
        for r in result:
            review_at = r['at']
            if isinstance(review_at, str):
                review_at = datetime.fromisoformat(review_at)
            
            if review_at >= cutoff_date:
                all_captured.append({
                    'review_id': r.get('reviewId', ''),
                    'rating': r['score'],
                    'review_text': r['content'],
                    'date': review_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'app_id': app_id  # Store package ID in metadata
                })
        
        print(f"Found {len(all_captured)} total reviews so far.")

    if not all_captured:
        print("No reviews found for the given criteria.")
        return

    df = pd.DataFrame(all_captured)
    
    # Save to the expected raw data path
    output_path = "data/raw/shein_reviews_raw.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Successfully scraped and saved {len(df)} reviews to {output_path}")

if __name__ == "__main__":
    import sys
    package_id = sys.argv[1] if len(sys.argv) > 1 else None
    run_scraper(package_id)
