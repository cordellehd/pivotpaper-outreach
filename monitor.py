#!/usr/bin/env python3
"""
monitor.py — Reply monitor for PivotPaper outreach.

Connects to the IONOS IMAP inbox, checks for replies from known prospects,
updates their status in the database, and sends a notification email with
the reply content and a suggested response draft.

Usage:
    python monitor.py [--db outreach.db] [--dry-run]

Environment variables required:
    SMTP_HOST     (default: smtp.ionos.com)
    SMTP_PORT     (default: 587)
    SMTP_USER     (default: cc@pivotpaper.us)
    SMTP_PASSWORD (required)
    IMAP_HOST     (default: imap.ionos.com)
    IMAP_PORT     (default: 993)
"""

import argparse
import email
import imaplib
import logging
import os
import re
import smtplib
import sqlite3
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# --- Configuration ---
SCRIPT_DIR = Path(__file__).parent
DEFAULT_DB = SCRIPT_DIR / "outreach.db"
LOG_FILE = SCRIPT_DIR / "outreach.log"
NOTIFICATION_EMAIL = "cc@pivotpaper.us"

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


def get_known_prospects(conn: sqlite3.Connection) -> dict:
    """Return a dict mapping email -> prospect info for all prospects in the DB."""
    cursor = conn.execute(
        "SELECT DISTINCT email, first_name, last_name, segment FROM outreach"
    )
    prospects = {}
    for row in cursor.fetchall():
        prospects[row[0].lower()] = {
            "email": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "segment": row[3],
        }
    return prospects


def mark_as_replied(conn: sqlite3.Connection, prospect_email: str):
    """Update all records for this prospect to 'replied' status."""
    conn.execute(
        "UPDATE outreach SET status = 'replied' WHERE email = ?",
        (prospect_email,),
    )
    conn.commit()


def extract_body(msg) -> str:
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")
            elif content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    # Strip HTML tags for notification
                    text = payload.decode("utf-8", errors="replace")
                    text = re.sub(r"<[^>]+>", "", text)
                    return text.strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="replace")
    return "(Unable to extract body)"


def generate_response_draft(prospect: dict, reply_content: str) -> str:
    """Generate a suggested response draft based on the prospect's segment and reply."""
    first_name = prospect["first_name"]
    segment = prospect["segment"]

    # Simple keyword-based response suggestions
    reply_lower = reply_content.lower()

    if any(word in reply_lower for word in ["interested", "yes", "sure", "tell me more", "send it"]):
        return f"""Hi {first_name},

Thanks so much for getting back to me! I'd love to help.

Here's what I suggest as a next step: let's do a quick 15-minute call where I can learn about your background and goals. I'll also take a look at your current resume and give you some immediate feedback.

Would [suggest 2-3 time slots] work for you?

Best,
The PivotPaper Team"""

    elif any(word in reply_lower for word in ["how much", "price", "cost", "pricing", "rates"]):
        return f"""Hi {first_name},

Great question! Our packages start at:
- Resume Refresh (light edit + ATS optimization): $149
- Full Resume Rewrite: $299
- Premium Package (resume + cover letter + LinkedIn): $449

All packages include one round of revisions and a 60-day interview guarantee.

Would you like to schedule a free consultation to discuss which option fits your needs?

Best,
The PivotPaper Team"""

    elif any(word in reply_lower for word in ["unsubscribe", "stop", "remove", "no thanks"]):
        return f"""Hi {first_name},

Absolutely — I've removed you from our list. No more emails from us.

Wishing you the best in your career. If you ever need help down the road, don't hesitate to reach out.

Best,
The PivotPaper Team"""

    else:
        return f"""Hi {first_name},

Thanks for your reply! I appreciate you taking the time to respond.

I'd love to continue the conversation. Would you be open to a quick 10-15 minute call to discuss how we can help with your resume?

Let me know what works for your schedule.

Best,
The PivotPaper Team"""


def send_notification(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    prospect: dict,
    reply_content: str,
    response_draft: str,
    dry_run: bool = False,
) -> bool:
    """Send notification email about the reply to the team."""
    subject = f"New Reply from {prospect['first_name']} {prospect['last_name']} ({prospect['segment']})"

    body = f"""<html><body>
<h2>New Reply Received!</h2>

<table style="border-collapse:collapse; margin-bottom:20px;">
<tr><td style="padding:5px 15px 5px 0; font-weight:bold;">Name:</td><td>{prospect['first_name']} {prospect['last_name']}</td></tr>
<tr><td style="padding:5px 15px 5px 0; font-weight:bold;">Email:</td><td>{prospect['email']}</td></tr>
<tr><td style="padding:5px 15px 5px 0; font-weight:bold;">Segment:</td><td>{prospect['segment']}</td></tr>
<tr><td style="padding:5px 15px 5px 0; font-weight:bold;">Time:</td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
</table>

<h3>Their Reply:</h3>
<div style="background:#f5f5f5; padding:15px; border-left:3px solid #2196F3; margin:10px 0;">
<pre style="white-space:pre-wrap; font-family:inherit;">{reply_content}</pre>
</div>

<h3>Suggested Response Draft:</h3>
<div style="background:#f0fff0; padding:15px; border-left:3px solid #4CAF50; margin:10px 0;">
<pre style="white-space:pre-wrap; font-family:inherit;">{response_draft}</pre>
</div>

<p><em>Review and personalize before sending.</em></p>
</body></html>"""

    if dry_run:
        logger.info(f"[DRY RUN] Would send notification about reply from {prospect['email']}")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = NOTIFICATION_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, NOTIFICATION_EMAIL, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False


def check_inbox(
    imap_host: str,
    imap_port: int,
    imap_user: str,
    imap_password: str,
    conn: sqlite3.Connection,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    dry_run: bool = False,
):
    """Connect to IMAP, check for replies from known prospects."""
    known_prospects = get_known_prospects(conn)
    if not known_prospects:
        logger.info("No prospects in database yet.")
        return

    logger.info(f"Checking inbox for replies from {len(known_prospects)} known prospects...")

    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(imap_user, imap_password)
        mail.select("INBOX")

        # Search for unseen messages
        status, message_ids = mail.search(None, "UNSEEN")
        if status != "OK":
            logger.error("Failed to search inbox")
            return

        ids = message_ids[0].split()
        logger.info(f"Found {len(ids)} unread messages")

        replies_found = 0
        for msg_id in ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract sender email
            from_header = msg.get("From", "")
            # Parse email from "Name <email>" or plain "email" format
            match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", from_header)
            if not match:
                continue

            sender_email = match.group(0).lower()

            # Check if sender is a known prospect
            if sender_email in known_prospects:
                prospect = known_prospects[sender_email]
                reply_content = extract_body(msg)
                response_draft = generate_response_draft(prospect, reply_content)

                logger.info(f"Reply detected from {prospect['first_name']} {prospect['last_name']} ({sender_email})")

                # Update status in DB
                if not dry_run:
                    mark_as_replied(conn, sender_email)

                # Send notification
                send_notification(
                    smtp_host, smtp_port, smtp_user, smtp_password,
                    prospect, reply_content, response_draft, dry_run=dry_run,
                )

                # Mark as read
                if not dry_run:
                    mail.store(msg_id, "+FLAGS", "\\Seen")

                replies_found += 1

        logger.info(f"Processed {replies_found} replies from prospects.")
        mail.logout()

    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error checking inbox: {e}")


def main():
    parser = argparse.ArgumentParser(description="PivotPaper reply monitor")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument("--dry-run", action="store_true", help="Don't modify DB or mark emails")
    args = parser.parse_args()

    # Load credentials
    smtp_host = os.environ.get("SMTP_HOST", "smtp.ionos.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "cc@pivotpaper.us")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    imap_host = os.environ.get("IMAP_HOST", "imap.ionos.com")
    imap_port = int(os.environ.get("IMAP_PORT", "993"))

    if not smtp_password and not args.dry_run:
        logger.error("SMTP_PASSWORD environment variable is required")
        sys.exit(1)

    # Open database
    db_path = args.db
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}. Run outreach.py first.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)

    check_inbox(
        imap_host, imap_port, smtp_user, smtp_password or "",
        conn,
        smtp_host, smtp_port, smtp_user, smtp_password or "",
        dry_run=args.dry_run,
    )

    conn.close()


if __name__ == "__main__":
    main()
