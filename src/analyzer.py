import pandas as pd
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline

def load_taxonomy():
    taxonomy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "product_taxonomy.json")
    with open(taxonomy_path, "r") as f:
        return json.load(f)

def map_cluster_to_taxonomy(cluster_reviews, taxonomy):
    """Deterministic keyword-based mapping logic."""
    # Extract top keywords/phrases from the cluster
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10, ngram_range=(1, 2))
    try:
        vectorizer.fit(cluster_reviews)
        cluster_terms = vectorizer.get_feature_names_out()
    except:
        cluster_terms = []

    best_theme = "Other / Emerging Issues"
    max_score = 0
    
    threshold = 0.1 # Minimum overlap score to avoid random mapping

    for theme_name, info in taxonomy.items():
        score = 0
        taxonomy_keywords = info["keywords"]
        
        for term in cluster_terms:
            # Check for direct or partial matches
            for kw in taxonomy_keywords:
                if kw in term or term in kw:
                    score += 1
        
        # Normalize score by number of keywords (optional) or just use raw count
        if score > max_score:
            max_score = score
            best_theme = theme_name

    if max_score < 1: # Strict threshold
         best_theme = "Other / Emerging Issues"
         
    return best_theme

def get_llm_description(theme_name, samples):
    """Use LLM only for phrasing descriptions as per Objective 1."""
    try:
        print(f"Generating description for theme: {theme_name}")
        model_name = "distilgpt2"
        generator = pipeline("text-generation", model=model_name, device=-1)
        
        text = " | ".join(samples[:3])
        prompt = f"Category: {theme_name}\nReviews: {text}\nSummary of issues: "
        
        result = generator(prompt, max_new_tokens=40, do_sample=False)
        desc = result[0]['generated_text'][len(prompt):].split("\n")[0].strip()
        return desc[:150]
    except Exception as e:
        print(f"LLM Description failed: {e}")
        return None

def discover_themes(df, num_themes=10): # We start with more clusters and then merge
    print(f"--- Task 3 (Product Taxonomy Update): Theme Discovery ---")
    
    processed_mapping_path = "data/processed/reviews_with_themes.csv"
    os.makedirs("data/processed", exist_ok=True)
    
    # 1. Generate Embeddings
    print("Generating embeddings using all-MiniLM-L6-v2...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(df['review_text'].tolist(), show_progress_bar=True)
    
    # 2. Semantic Clustering (Deterministic step)
    print(f"Clustering into {num_themes} semantic groups...")
    kmeans = KMeans(n_clusters=num_themes, random_state=42, n_init=10)
    df['cluster_id'] = kmeans.fit_predict(embeddings)
    
    taxonomy = load_taxonomy()
    
    # 3. Layer 2: Map to Taxonomy
    print("Mapping clusters to product taxonomy...")
    cluster_to_theme = {}
    for i in range(num_themes):
        cluster_reviews = df[df['cluster_id'] == i]['review_text']
        theme_name = map_cluster_to_taxonomy(cluster_reviews, taxonomy)
        cluster_to_theme[i] = theme_name
        
    df['theme_name'] = df['cluster_id'].map(cluster_to_theme)
    
    # 4. Merge clusters by theme
    themes_data = []
    final_theme_groups = df.groupby('theme_name')
    
    for theme_name, group in final_theme_groups:
        # Get description
        taxonomy_info = taxonomy.get(theme_name, {"description": "Emerging issues or uncategorized feedback."})
        description = taxonomy_info["description"]
        
        # Optionally refine description with LLM
        # samples = group['review_text'].sample(min(len(group), 5)).tolist()
        # llm_desc = get_llm_description(theme_name, samples)
        # if llm_desc: description = llm_desc

        themes_data.append({
            "theme_name": theme_name,
            "description": description,
            "count": len(group)
        })
        
    # Sort themes by volume
    themes_data = sorted(themes_data, key=lambda x: x['count'], reverse=True)
    
    # Objective 1: Persist mapping
    output_df = df.copy()
    if 'review_id' not in output_df.columns:
        output_df['review_id'] = [f"rev_{i}" for i in range(len(output_df))]
    
    # Ensure theme_id is consistent for this run (just use index in sorted themes)
    theme_id_map = {t['theme_name']: i for i, t in enumerate(themes_data)}
    output_df['theme_id'] = output_df['theme_name'].map(theme_id_map)
    
    cols_to_save = ['review_id', 'date', 'rating', 'review_text', 'theme_id', 'theme_name']
    output_df[cols_to_save].to_csv(processed_mapping_path, index=False)
    print(f"Saved review-to-theme mapping to {processed_mapping_path}")
    
    return output_df, themes_data, embeddings

def select_quotes(df, themes):
    print("--- Task 4 (Product Taxonomy Update): Quote Selection ---")
    selected_quotes = []
    
    for theme in themes[:5]: # Max 5 themes
        theme_name = theme['theme_name']
        theme_reviews = df[df['theme_name'] == theme_name]
        
        # Get 3 representative reviews as per Objective 3
        # Simplification: get the most "central" ones or just samples if embeddings not passed
        # Here we just sample 3 and trim them
        reps = theme_reviews.sample(min(len(theme_reviews), 3), random_state=42)
        
        quotes_list = []
        for _, row in reps.iterrows():
            text = row['review_text']
            if len(text) > 200:
                text = text[:197] + "..."
            quotes_list.append({
                "rating": row['rating'],
                "quote": text
            })
            
        selected_quotes.append({
            "theme": theme_name,
            "quotes": quotes_list
        })
        
    return selected_quotes
