#!/usr/bin/env python3
"""
followup.py — Follow-up email sender for PivotPaper outreach.

Checks the outreach database for prospects who haven't replied and sends
the appropriate follow-up email based on timing:
  - Email 2: 3 days after Email 1
  - Email 3: 7 days after Email 1 (value-add email)
  - Email 4: 14 days after Email 1 (soft close)

Usage:
    python followup.py [--db outreach.db] [--limit 50] [--dry-run]

Environment variables required:
    SMTP_HOST     (default: smtp.ionos.com)
    SMTP_PORT     (default: 587)
    SMTP_USER     (default: cc@pivotpaper.us)
    SMTP_PASSWORD (required)
"""

import argparse
import logging
import os
import random
import smtplib
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from templates import get_template

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
DEFAULT_DB = SCRIPT_DIR / "outreach.db"
LOG_FILE = SCRIPT_DIR / "outreach.log"

# Follow-up schedule: (email_number_to_send, days_since_previous_email_1)
FOLLOWUP_SCHEDULE = [
    (2, 3),   # Send Email 2 three days after Email 1
    (3, 7),   # Send Email 3 seven days after Email 1
    (4, 14),  # Send Email 4 fourteen days after Email 1
]

MIN_DELAY = 30
MAX_DELAY = 90

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def get_followup_candidates(conn: sqlite3.Connection, email_number: int, days_ago: int) -> list:
    """
    Find prospects who:
    - Received email (email_number - 1) exactly `days_ago` or more days ago
    - Have NOT received email_number yet
    - Have NOT replied (status != 'replied')
    """
    cutoff_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
    prev_email_number = email_number - 1

    query = """
        SELECT o.email, o.first_name, o.last_name, o.segment
        FROM outreach o
        WHERE o.email_number = ?
          AND o.sent_at <= ?
          AND o.status != 'replied'
          AND NOT EXISTS (
              SELECT 1 FROM outreach o2
              WHERE o2.email = o.email AND o2.email_number = ?
          )
          AND NOT EXISTS (
              SELECT 1 FROM outreach o3
              WHERE o3.email = o.email AND o3.status = 'replied'
          )
    """
    cursor = conn.execute(query, (prev_email_number, cutoff_date, email_number))
    return [
        {
            "email": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "segment": row[3],
        }
        for row in cursor.fetchall()
    ]


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    to_email: str,
    subject: str,
    html_body: str,
    dry_run: bool = False,
) -> bool:
    """Send a single HTML email via SMTP."""
    if dry_run:
        logger.info(f"[DRY RUN] Would send to {to_email}: {subject}")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = smtp_user

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Failed to send to {to_email}: {e}")
        return False


def record_followup(conn: sqlite3.Connection, email: str, first_name: str, last_name: str, segment: str, email_number: int):
    """Record a follow-up send in the database."""
    conn.execute(
        """INSERT OR IGNORE INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (email, first_name, last_name, segment, email_number, datetime.now().isoformat(), "sent"),
    )
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="PivotPaper follow-up email sender")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument("--limit", type=int, default=50, help="Max emails per run")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send emails")
    args = parser.parse_args()

    # Load credentials
    smtp_host = os.environ.get("SMTP_HOST", "smtp.ionos.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "cc@pivotpaper.us")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_password and not args.dry_run:
        logger.error("SMTP_PASSWORD environment variable is required")
        sys.exit(1)

    # Open database
    db_path = args.db
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}. Run outreach.py first.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    total_sent = 0

    for email_number, days_ago in FOLLOWUP_SCHEDULE:
        if total_sent >= args.limit:
            break

        candidates = get_followup_candidates(conn, email_number, days_ago)
        logger.info(f"Email {email_number} (>{days_ago} days): {len(candidates)} candidates")

        for prospect in candidates:
            if total_sent >= args.limit:
                break

            email = prospect["email"]
            first_name = prospect["first_name"]
            last_name = prospect["last_name"]
            segment = prospect["segment"]

            # Get template
            template = get_template(segment, email_number)
            subject = template["subject"].format(first_name=first_name)
            body = template["body"].format(first_name=first_name)

            # Send
            success = send_email(
                smtp_host, smtp_port, smtp_user, smtp_password or "",
                email, subject, body, dry_run=args.dry_run,
            )

            if success:
                record_followup(conn, email, first_name, last_name, segment, email_number)
                total_sent += 1
                logger.info(
                    f"[{total_sent}] Sent Email {email_number} to {email} "
                    f"(segment: {segment})"
                )

                # Random delay
                if not args.dry_run:
                    delay = random.randint(MIN_DELAY, MAX_DELAY)
                    logger.info(f"Waiting {delay}s before next send...")
                    time.sleep(delay)
            else:
                logger.error(f"Failed to send Email {email_number} to {email}")

    logger.info(f"Follow-up session complete. Sent {total_sent} emails total.")
    conn.close()


if __name__ == "__main__":
    main()
