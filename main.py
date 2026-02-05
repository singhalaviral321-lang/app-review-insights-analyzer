import os
import json
import pandas as pd
from src.data_processor import load_and_validate, clean_reviews
from src.analyzer import discover_themes, select_quotes
from src.report_gen import generate_reports, generate_detailed_breakdown

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def main():
    config = load_config()
    app_name = config.get("APP_NAME", "App")
    print(f"=== {app_name} Weekly Review Analyzer ===")
    
    # Paths
    raw_path = "data/raw/shein_reviews_raw.csv"
    processed_path = "data/processed/reviews_clean.csv"
    mapping_path = "data/processed/reviews_with_themes.csv"
    
    # 1. Ingestion & Validation
    df_raw = load_and_validate(raw_path)
    
    # 2. Cleaning
    df_clean = clean_reviews(df_raw, processed_path)
    
    # 3. Theme Discovery (Two-Layer Product Taxonomy)
    df_analyzed, themes, embeddings = discover_themes(df_clean)
    
    # 4. Quote Selection (Refined)
    quotes = select_quotes(df_analyzed, themes)
    
    # 5 & 6. Report Generation
    generate_reports(df_analyzed, themes, quotes)
    
    # Detailed Theme Breakdown (PDF & MD)
    df_mapping = pd.read_csv(mapping_path)
    generate_detailed_breakdown(df_mapping, themes)
    
    print("\nAll tasks completed successfully.")

if __name__ == "__main__":
    main()
