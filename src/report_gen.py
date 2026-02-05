import os
import json
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF

ACTION_TEMPLATES = {
    "Payments & Refunds": "Improve refund transparency by surfacing real-time refund status and reducing turnaround time for wrong-item cases.",
    "Delivery & Logistics": "Identify regions with repeated delivery delays and work with logistics partners to improve SLA adherence.",
    "Wrong / Missing Items": "Reduce wrong-item incidents by auditing high-frequency SKU mismatches and improving warehouse quality checks.",
    "Returns & Customer Support": "Shorten resolution time by prioritizing return pickup failures and improving first-response time.",
    "App Experience & Stability": "Prioritize fixes for high-impact crashes and checkout issues across iOS and Android devices.",
    "Product Quality & Pricing": "Review supplier quality metrics and improve size and material clarity on product detail pages.",
    "Other / Emerging Issues": "Monitor emerging feedback clusters for new friction points and initiate deep-dive analysis if volume increases."
}

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def generate_reports(df, themes, quotes):
    print("--- Task 5 & 6 (Upgraded): Report Generation ---")
    config = load_config()
    app_name = config.get("APP_NAME", "App")
    
    # 1. Prepare data
    start_date = pd.to_datetime(df['date']).min().strftime("%b %d, %Y")
    end_date = pd.to_datetime(df['date']).max().strftime("%b %d, %Y")
    week_str = pd.to_datetime(df['date']).max().strftime("%d %b %Y")
    
    # Rating Distribution (Objective 6)
    total = len(df)
    low_stars = len(df[df['rating'] <= 2])
    mid_stars = len(df[df['rating'] == 3])
    high_stars = len(df[df['rating'] >= 4])
    
    dist = {
        "1-2": round((low_stars / total) * 100),
        "3": round((mid_stars / total) * 100),
        "4-5": round((high_stars / total) * 100)
    }

    # Task 5: Weekly Insight Note
    note_content = f"# {app_name} — Weekly App Review Pulse\n"
    note_content += f"Period: {start_date} - {end_date}\n\n"
    note_content += "## Top Themes\n"
    for i, t in enumerate(themes[:3], 1):
        note_content += f"{i}. {t['theme_name']}: {t['count']} reviews\n"
    
    note_content += "\n## What Users Are Saying\n"
    for t_quote in quotes[:3]:
        for q in t_quote['quotes']:
             note_content += f"• [{t_quote['theme']}] \"{q['quote']}\"\n"
        
    note_content += "\n## Action Ideas\n"
    for i, t in enumerate(themes[:3], 1):
        action = ACTION_TEMPLATES.get(t['theme_name'], "Investigate user concerns.")
        note_content += f"{i}. {action}\n"
    
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/weekly_note.md", "w", encoding='utf-8') as f:
        f.write(note_content.strip())
    print("Saved weekly_note.md")

    # Task 6: Email Draft (Updated Objective 6)
    email_content = f"Subject: {app_name} — Weekly App Review Pulse ({week_str})\n\n"
    email_content += "Hi team,\n\n"
    email_content += f"Recent feedback for {app_name} highlights {themes[0]['theme_name']} and {themes[1]['theme_name']} as key focus areas.\n\n"
    
    email_content += "## Top Themes\n"
    for t in themes[:3]:
        email_content += f"- {t['theme_name']} ({t['count']} reviews)\n"
    
    email_content += "\n## Rating Distribution (This Period)\n"
    email_content += f"- 1–2★: {dist['1-2']}%\n"
    email_content += f"- 3★: {dist['3']}%\n"
    email_content += f"- 4–5★: {dist['4-5']}%\n\n"
    
    email_content += "## Action Ideas\n"
    for t in themes[:3]:
        action = ACTION_TEMPLATES.get(t['theme_name'], "Analyze emerging issues.")
        email_content += f"- {action}\n"
        
    email_content += "\nBest,\nProduct Manager"
    
    with open("outputs/email_draft.txt", "w", encoding='utf-8') as f:
        f.write(email_content.strip())
    print("Saved email_draft.txt")

def generate_detailed_breakdown(df_mapping, themes):
    """Objective 3: Exec-safe PDF breakdown."""
    print("--- Generating Detailed Theme Breakdown (PDF) ---")
    config = load_config()
    app_name = config.get("APP_NAME", "App")
    
    md_content = f"# Detailed Theme Breakdown — {app_name}\n\n"
    total_all = len(df_mapping)
    
    # Global Star Distribution (Rounded whole %)
    g_low = round((len(df_mapping[df_mapping['rating'] <= 2]) / total_all) * 100) if total_all > 0 else 0
    g_mid = round((len(df_mapping[df_mapping['rating'] == 3]) / total_all) * 100) if total_all > 0 else 0
    g_high = round((len(df_mapping[df_mapping['rating'] >= 4]) / total_all) * 100) if total_all > 0 else 0

    # -------- PDF Setup (Unicode-safe) --------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    FONT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets",
        "fonts",
        "DejaVuSans.ttf"
    )

    if os.path.exists(FONT_PATH):
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.add_font("DejaVu", "B", FONT_PATH, uni=True)
        pdf.add_font("DejaVu", "I", FONT_PATH, uni=True)
        font_family = "DejaVu"
    else:
        print("Warning: DejaVuSans.ttf not found. Falling back to Arial.")
        font_family = "Arial"

    # Title Layer
    pdf.set_font(font_family, "B", 16)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 10, f"Detailed Theme Breakdown — {app_name}" )
    pdf.ln(5)
    
    for theme in themes[:5]:
        t_name = theme['theme_name']
        t_desc = theme['description']
        
        t_df = df_mapping[df_mapping['theme_name'] == t_name]
        count = len(t_df)
        percent = (count / total_all) * 100 if total_all > 0 else 0
        
        # MD Content
        md_content += f"### Theme: {t_name}\n"
        md_content += f"**Why this matters:** {t_desc}\n\n"
        md_content += f"**Volume:**\n- Total reviews: {count}\n- % of total: {percent:.1f}%\n"
        md_content += f"**Star Distribution (Overall Period):**\n- 1–2★: {g_low}%\n- 3★: {g_mid}%\n- 4–5★: {g_high}%\n\n"
        md_content += "**Representative Reviews:**\n"
        
        reps = t_df.sample(min(len(t_df), 3), random_state=42)
        for _, row in reps.iterrows():
            stars = "★" * int(row['rating'])
            md_content += f"- {stars} \"{row['review_text'][:150]}...\"\n"
        md_content += "\n---\n\n"
        
        # PDF Section - Strict Left Alignment
        pdf.set_x(pdf.l_margin)
        pdf.set_font(font_family, "B", 13)
        pdf.multi_cell(0, 8, f"Theme: {t_name}" )
        pdf.ln(1)

        pdf.set_x(pdf.l_margin)
        pdf.set_font(font_family, "B", 10)
        pdf.multi_cell(0, 6, "Why this matters:" )
        pdf.set_font(font_family, "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, t_desc )
        pdf.ln(3)

        pdf.set_x(pdf.l_margin)
        pdf.set_font(font_family, "B", 10)
        pdf.multi_cell(0, 6, "Volume:" )
        pdf.set_font(font_family, "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, f"{count} reviews ({percent:.1f}%)" )
        pdf.ln(3)

        pdf.set_x(pdf.l_margin)
        pdf.set_font(font_family, "B", 10)
        pdf.multi_cell(0, 6, "Star Distribution (Overall Period):" )
        pdf.set_font(font_family, "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, f"1–2★: {g_low}%" )
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, f"3★: {g_mid}%" )
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, f"4–5★: {g_high}%" )
        pdf.ln(3)

        pdf.set_x(pdf.l_margin)
        pdf.set_font(font_family, "B", 10)
        pdf.multi_cell(0, 6, "Representative Reviews:" )
        pdf.set_font(font_family, "", 9)
        for _, row in reps.iterrows():
            stars = "★" * int(row["rating"])
            text = row["review_text"]
            if len(text) > 250: text = text[:247] + "..."
            
            try:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, f"- [{stars}] {text}" )
                pdf.ln(1)
            except:
                 pdf.set_x(pdf.l_margin)
                 pdf.multi_cell(0, 5, f"- [{stars}] [Internal formatting error]" )

        pdf.ln(8)

    with open("outputs/detailed_theme_breakdown.md", "w", encoding='utf-8') as f:
        f.write(md_content)
        
    try:
        pdf_path = "outputs/detailed_theme_breakdown.pdf"
        pdf.output(pdf_path)
        print(f"Saved {pdf_path}")
    except Exception as e:
        print(f"PDF generation failed: {e}")
