import os
import sys
import subprocess
import logging
import argparse
import json
from datetime import datetime
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# =========================================================
# Logging setup
# =========================================================

LOG_DIR = os.path.join(os.getcwd(), "outputs", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(
    LOG_DIR,
    f"weekly_run_{datetime.now().strftime('%Y%m%d')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

# =========================================================
# Email helper (SIDE EFFECTS LIVE HERE)
# =========================================================

def send_email_with_attachment(subject, body, attachment_path):
    load_dotenv()

    email_host = os.getenv("EMAIL_HOST")
    email_port = os.getenv("EMAIL_PORT")
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_to = os.getenv("EMAIL_TO")

    if not all([email_host, email_port, email_user, email_password, email_to]):
        logging.error("Email environment variables are not fully set. Skipping email.")
        return

    if not os.path.exists(attachment_path):
        logging.error(f"Attachment not found at {attachment_path}. Email not sent.")
        return

    try:
        email_port = int(email_port)
    except ValueError:
        logging.error("EMAIL_PORT is not a valid integer. Email not sent.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = email_to
    msg.set_content(body)

    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="pdf",
        filename=file_name,
    )

    try:
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)

        logging.info("Weekly email sent successfully.")

    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

# =========================================================
# Script runner utility
# =========================================================

def run_script(script_path, description):
    logging.info(f"Starting {description}: {script_path}")

    python_exe = sys.executable  # ensures venv python is used

    try:
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            check=True,
        )
        logging.info(f"Finished {description} successfully.")

        if result.stdout:
            logging.debug(f"Output:\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error during {description}:")
        logging.error(f"Exit code: {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        logging.error(f"Stdout: {e.stdout}")
        sys.exit(1)

    except Exception as e:
        logging.error(f"Unexpected error running {description}: {str(e)}")
        sys.exit(1)

# =========================================================
# Main orchestrator
# =========================================================

def main():
    parser = argparse.ArgumentParser(
        description="SHEIN India Weekly Review Analyzer Orchestrator"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with mock data instead of real scraping",
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    logging.info("==========================================")
    logging.info(f"Weekly Run Started (Test Mode: {args.test})")
    logging.info("==========================================")

    # Step 1: Data ingestion
    if args.test:
        mock_gen_path = os.path.join(base_dir, "demo", "generate_mock_data.py")
        run_script(mock_gen_path, "Mock Data Generation")
    else:
        scraper_path = os.path.join(base_dir, "src", "scrape_shein_india.py")
        run_script(scraper_path, "Real Review Scraping")

    # Step 2: Analysis & report generation
    main_pipeline_path = os.path.join(base_dir, "main.py")
    run_script(main_pipeline_path, "Review Analysis & Report Generation")

    logging.info("==========================================")
    logging.info("Weekly Run Completed Successfully")
    logging.info("==========================================")
    logging.info(f"Outputs generated in {os.path.join(base_dir, 'outputs')}")

    # Step 3: Email delivery (SIDE EFFECT)
    if not args.test:
        weekly_note_path = os.path.join(base_dir, "outputs", "weekly_note.md")
        detailed_pdf_path = os.path.join(
            base_dir, "outputs", "detailed_theme_breakdown.pdf"
        )

        if os.path.exists(weekly_note_path) and os.path.exists(detailed_pdf_path):
            with open(weekly_note_path, "r", encoding="utf-8") as f:
                email_body = f.read()

            config_path = os.path.join(base_dir, "config", "config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
            app_name = config.get("APP_NAME", "App")

            subject = (
                f"{app_name} — Weekly App Review Pulse "
                f"({datetime.now().strftime('%d %b %Y')})"
            )

            logging.info("Sending weekly email...")
            send_email_with_attachment(
                subject=subject,
                body=email_body,
                attachment_path=detailed_pdf_path,
            )
        else:
            logging.error(
                "Email not sent: weekly_note.md or detailed_theme_breakdown.pdf missing."
            )

# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    main()
