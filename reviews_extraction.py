import argparse
import csv
import json
import sys
import os
from datetime import datetime, timedelta
from google_play_scraper import reviews, Sort

def scrape_reviews(app_id, count, lang, country, sort_order, score, output_file, format_type, overwrite):
    sort_map = {
        'newest': Sort.NEWEST,
        'relevant': Sort.MOST_RELEVANT,
        'rating': Sort.RATING
    }
    
    print(f"Fetching up to {count} reviews for {app_id} (Lang: {lang}, Country: {country})...")
    
    all_reviews = []
    continuation_token = None
    
    # We fetch in batches if count is high
    batches = (count // 100) + 1
    
    for _ in range(batches):
        result, continuation_token = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=sort_map.get(sort_order, Sort.NEWEST),
            count=min(count - len(all_reviews), 100),
            filter_score_with=score,
            continuation_token=continuation_token
        )
        all_reviews.extend(result)
        if not continuation_token or len(all_reviews) >= count:
            break

    if not all_reviews:
        print("Empty output – the chosen locale or filters might not have any reviews.")
        return

    # Filter to requested count in case of overlap
    all_reviews = all_reviews[:count]

    # Save logic
    if not overwrite and output_file and os.path.exists(output_file):
        print(f"Error: {output_file} already exists. Use --overwrite to replace.")
        sys.exit(1)

    if format_type == 'json':
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_reviews, f, indent=2, default=str)
            print(f"Saved {len(all_reviews)} reviews to {output_file}")
        else:
            print(json.dumps(all_reviews, indent=2, default=str))
    else:
        # CSV Format
        fieldnames = [
            'review_id', 'user_name', 'user_image', 'score', 'thumbs_up_count',
            'review_created_version', 'app_version', 'content', 'reply_content',
            'at', 'replied_at'
        ]
        
        # Map scraper keys to requested field names
        # Scraper returns: reviewId, userName, userImage, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt, appVersion
        mapping = {
            'reviewId': 'review_id',
            'userName': 'user_name',
            'userImage': 'user_image',
            'score': 'score',
            'thumbsUpCount': 'thumbs_up_count',
            'reviewCreatedVersion': 'review_created_version',
            'appVersion': 'app_version',
            'content': 'content',
            'replyContent': 'reply_content',
            'at': 'at',
            'repliedAt': 'replied_at'
        }

        output_path = output_file if output_file else f"{app_id.replace('.', '_')}_reviews.csv"
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in all_reviews:
                row = {mapping.get(k, k): v for k, v in r.items() if mapping.get(k, k) in fieldnames}
                writer.writerow(row)
        
        print(f"Saved {len(all_reviews)} reviews to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Google Play Store Review Extractor')
    parser.add_argument('app_id', help='App ID (e.g. com.ril.shein)')
    parser.add_argument('--count', '-n', type=int, default=200, help='Max reviews to fetch')
    parser.add_argument('--lang', default='en', help='Language code')
    parser.add_argument('--country', default='us', help='Country code')
    parser.add_argument('--sort', default='newest', choices=['newest', 'relevant', 'rating'], help='Sort order')
    parser.add_argument('--score', type=int, choices=[1, 2, 3, 4, 5], help='Filter by star rating')
    parser.add_argument('--format', default='csv', choices=['csv', 'json'], help='Output format')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing file')

    args = parser.parse_args()

    scrape_reviews(
        args.app_id, args.count, args.lang, args.country,
        args.sort, args.score, args.output, args.format, args.overwrite
    )

if __name__ == "__main__":
    main()
