# App Review Insights Analyzer (Production Grade)

An automated tool for transforming App Store reviews into product-grade insights using semantic clustering and fixed taxonomy mapping.

## ✨ Features
- **Two-Layer Theme System**: Combines bottom-up semantic clustering with top-down Product Taxonomy mapping.
- **Configurable**: Work with any app via `config/config.json`.
- **PM-Grade Outputs**: Generates executive-ready emails and detailed PDF breakdown reports.
- **Privacy-First**: Automatic PII removal and noise cleaning.
- **Deterministic**: Uses fixed taxonomy and templates for reliable, professional language.

## 📁 Project Structure
- `config/config.json`: App naming and package ID setup.
- `config/product_taxonomy.json`: Definable product surface taxonomy with keywords.
- `src/analyzer.py`: Two-layer mapping logic (Clusters -> Taxonomy).
- `src/report_gen.py`: Email, Markdown, and PDF report generation.
- `src/scraper.py`: Configurable Google Play scraper.
- `run_weekly.py`: Orchestrator with logging and automated email delivery.

## 🚀 Getting Started

### 1. Configuration
Update `config/config.json` with your target app:
```json
{
  "APP_PACKAGE_ID": "com.ril.shein",
  "APP_NAME": "SHEIN India"
}
```

### 2. Taxonomy Enrichment
Modify `config/product_taxonomy.json` to add new categories or refine keywords. The system uses these keywords to map semantic clusters to themes.

### 3. Execution
```powershell
# Run the full pipeline
python run_weekly.py

# Run in test mode with taxonomy-aligned mock data
python run_weekly.py --test
```

## 🛠 Adding a New Industry
1. Update `APP_NAME` and `APP_PACKAGE_ID` in `config/config.json`.
2. Enrich `config/product_taxonomy.json` with industry-specific surfaces (e.g., for Fintech: "KYC & Verification", "Account Security").
3. Update `ACTION_TEMPLATES` in `src/report_gen.py` to provide relevant action ideas for your new categories.

## 📄 Outputs
- `outputs/weekly_note.md`: Internal VOC capture.
- `outputs/email_draft.txt`: Executive summary with rating distribution.
- `outputs/detailed_theme_breakdown.pdf`: Deep-dive artifact with "Why this matters" context.

---
*Created By Aviral Singhal*
