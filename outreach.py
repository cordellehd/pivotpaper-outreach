#!/usr/bin/env python3
"""
outreach.py — Cold email outreach sender for PivotPaper resume writing service.

Reads prospects from a CSV, sends the initial email (Email 1) based on their segment,
tracks everything in SQLite, respects daily limits, and adds random delays.

Usage:
    python outreach.py [--csv prospects.csv] [--db outreach.db] [--limit 50] [--dry-run]

Environment variables required:
    SMTP_HOST     (default: smtp.ionos.com)
    SMTP_PORT     (default: 587)
    SMTP_USER     (default: cc@pivotpaper.us)
    SMTP_PASSWORD (required)
"""

import argparse
import csv
import logging
import os
import random
import smtplib
import sqlite3
import sys
import time
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from templates import get_template, VALID_SEGMENTS

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
DEFAULT_CSV = SCRIPT_DIR / "prospects.csv"
DEFAULT_DB = SCRIPT_DIR / "outreach.db"
LOG_FILE = SCRIPT_DIR / "outreach.log"

# Delay between sends (seconds)
MIN_DELAY = 30
MAX_DELAY = 90

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize the SQLite database and create the outreach table if needed."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            segment TEXT NOT NULL,
            email_number INTEGER NOT NULL DEFAULT 1,
            sent_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'sent',
            UNIQUE(email, email_number)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_outreach_email ON outreach(email)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_outreach_status ON outreach(status)
    """)
    conn.commit()
    return conn


def get_today_send_count(conn: sqlite3.Connection) -> int:
    """Count how many emails were sent today."""
    today = date.today().isoformat()
    cursor = conn.execute(
        "SELECT COUNT(*) FROM outreach WHERE sent_at LIKE ?", (f"{today}%",)
    )
    return cursor.fetchone()[0]


def already_sent(conn: sqlite3.Connection, email: str, email_number: int) -> bool:
    """Check if this email+number combination was already sent."""
    cursor = conn.execute(
        "SELECT 1 FROM outreach WHERE email = ? AND email_number = ?",
        (email, email_number),
    )
    return cursor.fetchone() is not None


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
    """Send a single HTML email via SMTP. Returns True on success."""
    if dry_run:
        logger.info(f"[DRY RUN] Would send to {to_email}: {subject}")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = smtp_user

    # Attach HTML body
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


def record_send(
    conn: sqlite3.Connection,
    email: str,
    first_name: str,
    last_name: str,
    segment: str,
    email_number: int,
):
    """Record a sent email in the database."""
    conn.execute(
        """INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (email, first_name, last_name, segment, email_number, datetime.now().isoformat(), "sent"),
    )
    conn.commit()


def load_prospects(csv_path: str) -> list:
    """Load prospects from CSV. Returns list of dicts."""
    prospects = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Validate required fields
            if not all(row.get(k) for k in ["first_name", "last_name", "email", "segment"]):
                logger.warning(f"Skipping incomplete row: {row}")
                continue
            segment = row["segment"].strip().lower()
            if segment not in VALID_SEGMENTS:
                logger.warning(f"Skipping invalid segment '{segment}' for {row['email']}")
                continue
            prospects.append({
                "first_name": row["first_name"].strip(),
                "last_name": row["last_name"].strip(),
                "email": row["email"].strip().lower(),
                "segment": segment,
            })
    return prospects


def main():
    parser = argparse.ArgumentParser(description="PivotPaper cold outreach sender")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to prospects CSV")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument("--limit", type=int, default=50, help="Max emails per day")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send emails")
    args = parser.parse_args()

    # Load credentials from environment
    smtp_host = os.environ.get("SMTP_HOST", "smtp.ionos.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "cc@pivotpaper.us")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_password and not args.dry_run:
        logger.error("SMTP_PASSWORD environment variable is required")
        sys.exit(1)

    # Initialize database
    conn = init_db(args.db)

    # Check daily limit
    sent_today = get_today_send_count(conn)
    remaining = args.limit - sent_today
    if remaining <= 0:
        logger.info(f"Daily limit reached ({args.limit} emails). Try again tomorrow.")
        return

    logger.info(f"Daily budget: {remaining} emails remaining (sent {sent_today} today)")

    # Load prospects
    if not os.path.exists(args.csv):
        logger.error(f"CSV file not found: {args.csv}")
        sys.exit(1)

    prospects = load_prospects(args.csv)
    logger.info(f"Loaded {len(prospects)} prospects from {args.csv}")

    # Send emails
    sent_count = 0
    for prospect in prospects:
        if sent_count >= remaining:
            logger.info("Daily limit reached during this run.")
            break

        email = prospect["email"]
        first_name = prospect["first_name"]
        last_name = prospect["last_name"]
        segment = prospect["segment"]

        # Skip if already sent Email 1
        if already_sent(conn, email, 1):
            logger.debug(f"Already sent Email 1 to {email}, skipping")
            continue

        # Get template
        template = get_template(segment, 1)
        subject = template["subject"].format(first_name=first_name)
        body = template["body"].format(first_name=first_name)

        # Send
        success = send_email(
            smtp_host, smtp_port, smtp_user, smtp_password or "",
            email, subject, body, dry_run=args.dry_run,
        )

        if success:
            record_send(conn, email, first_name, last_name, segment, 1)
            sent_count += 1
            logger.info(f"[{sent_count}/{remaining}] Sent Email 1 to {email} (segment: {segment})")

            # Random delay between sends (skip for last email or dry run)
            if sent_count < remaining and not args.dry_run:
                delay = random.randint(MIN_DELAY, MAX_DELAY)
                logger.info(f"Waiting {delay}s before next send...")
                time.sleep(delay)
        else:
            logger.error(f"Failed to send to {email}")

    logger.info(f"Session complete. Sent {sent_count} emails.")
    conn.close()


if __name__ == "__main__":
    main()
