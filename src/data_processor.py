import os
import json
import pandas as pd
import re
import sys
from datetime import datetime, timedelta

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def load_and_validate(file_path):
    print(f"--- Task 1: Loading and Validating {file_path} ---")
    config = load_config()
    min_count = config.get("MIN_REVIEW_COUNT", 200)

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error: Failed to read CSV. {e}")
        sys.exit(1)
        
    required_cols = ['rating', 'review_text', 'date']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Missing required columns. Found: {df.columns.tolist()}")
        sys.exit(1)
        
    if len(df) < min_count:
        print(f"Error: Validation failed. Found {len(df)} reviews, need at least {min_count}.")
        sys.exit(1)
        
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        print(f"Error: Date parsing failed. {e}")
        sys.exit(1)
        
    print(f"Validation passed: {len(df)} reviews loaded.")
    return df

def clean_reviews(df, output_path):
    print("--- Task 2: Cleaning Reviews ---")
    config = load_config()
    weeks = config.get("DATE_RANGE_WEEKS", 8)
    
    # 1. Filter by date
    reference_date = datetime.now()
    cutoff_date = reference_date - timedelta(weeks=weeks)
    df = df[df['date'] >= cutoff_date].copy()
    print(f"Filtered to reviews since {cutoff_date.date()}: {len(df)} remaining.")
    
    # 2. PII and Noise Removal
    def remove_noise(text):
        if not isinstance(text, str):
            return ""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove Emails
        text = re.sub(r'\S+@\S+', '', text)
        # Remove Phone numbers
        text = re.sub(r'\+?\d[\d -]{8,}\d', '', text)
        # Remove common separators and noise
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    df['review_text'] = df['review_text'].apply(remove_noise)
    
    # 3. Basic cleanup
    df['review_text'] = df['review_text'].str.strip()
    
    # 4. Drop very short reviews
    df['word_count'] = df['review_text'].str.split().str.len()
    df = df[df['word_count'] >= 5].copy()
    print(f"Dropped short reviews (<5 words): {len(df)} remaining.")
    
    # Final cleanup
    df = df.drop(columns=['word_count'])
    
    # Save to processed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Cleaned reviews saved to {output_path}")
    return df

if __name__ == "__main__":
    raw_path = "data/raw/shein_reviews_raw.csv"
    processed_path = "data/processed/reviews_clean.csv"
    
    df = load_and_validate(raw_path)
    clean_df = clean_reviews(df, processed_path)
