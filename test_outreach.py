"""
Tests for the PivotPaper cold email outreach system.

Covers: templates, outreach.py, followup.py, and monitor.py logic.
Run with: python -m pytest test_outreach.py -x -q
"""

import csv
import os
import sqlite3
import smtplib
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))

from templates import get_template, VALID_SEGMENTS
import outreach
import followup
import monitor


# ============================================================
# Template Tests
# ============================================================

class TestTemplates:
    def test_all_segments_exist(self):
        """All declared segments have templates."""
        for segment in VALID_SEGMENTS:
            for email_num in range(1, 5):
                t = get_template(segment, email_num)
                assert "subject" in t
                assert "body" in t

    def test_personalization_placeholder(self):
        """All templates contain {first_name} placeholder."""
        for segment in VALID_SEGMENTS:
            for email_num in range(1, 5):
                t = get_template(segment, email_num)
                has_placeholder = (
                    "{first_name}" in t["subject"] or "{first_name}" in t["body"]
                )
                assert has_placeholder, f"{segment} email {email_num} missing personalization"

    def test_personalization_renders(self):
        """Templates render correctly with a name."""
        t = get_template("open_to_work", 1)
        subject = t["subject"].format(first_name="Alice")
        body = t["body"].format(first_name="Alice")
        assert "Alice" in subject
        assert "Alice" in body
        assert "{first_name}" not in subject
        assert "{first_name}" not in body

    def test_invalid_segment_raises(self):
        """Invalid segment raises ValueError."""
        with pytest.raises(ValueError):
            get_template("invalid_segment", 1)

    def test_invalid_email_number_raises(self):
        """Invalid email number raises ValueError."""
        with pytest.raises(ValueError):
            get_template("open_to_work", 5)

    def test_templates_are_html(self):
        """All template bodies contain HTML tags."""
        for segment in VALID_SEGMENTS:
            for email_num in range(1, 5):
                t = get_template(segment, email_num)
                assert "<html>" in t["body"] or "<p>" in t["body"]


# ============================================================
# Database Tests
# ============================================================

class TestDatabase:
    def setup_method(self):
        """Create a temp database for each test."""
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self.conn = outreach.init_db(self.db_path)

    def teardown_method(self):
        self.conn.close()
        os.unlink(self.db_path)

    def test_init_creates_table(self):
        """Database initialization creates the outreach table."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='outreach'"
        )
        assert cursor.fetchone() is not None

    def test_record_send(self):
        """Recording a send inserts a row correctly."""
        outreach.record_send(self.conn, "test@example.com", "Test", "User", "open_to_work", 1)
        cursor = self.conn.execute("SELECT * FROM outreach WHERE email = 'test@example.com'")
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "test@example.com"
        assert row[4] == "open_to_work"
        assert row[5] == 1

    def test_already_sent(self):
        """already_sent returns True for existing records."""
        outreach.record_send(self.conn, "test@example.com", "Test", "User", "open_to_work", 1)
        assert outreach.already_sent(self.conn, "test@example.com", 1) is True
        assert outreach.already_sent(self.conn, "test@example.com", 2) is False

    def test_daily_count(self):
        """get_today_send_count counts correctly."""
        outreach.record_send(self.conn, "a@test.com", "A", "User", "open_to_work", 1)
        outreach.record_send(self.conn, "b@test.com", "B", "User", "open_to_work", 1)
        count = outreach.get_today_send_count(self.conn)
        assert count == 2

    def test_unique_constraint(self):
        """Cannot insert duplicate email+email_number."""
        outreach.record_send(self.conn, "test@example.com", "Test", "User", "open_to_work", 1)
        with pytest.raises(sqlite3.IntegrityError):
            outreach.record_send(self.conn, "test@example.com", "Test", "User", "open_to_work", 1)


# ============================================================
# Prospect Loading Tests
# ============================================================

class TestProspectLoading:
    def test_load_valid_csv(self):
        """Loads a well-formed CSV correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "email", "segment"])
            writer.writerow(["Alice", "Smith", "alice@test.com", "open_to_work"])
            writer.writerow(["Bob", "Jones", "bob@test.com", "laid_off"])
            csv_path = f.name

        try:
            prospects = outreach.load_prospects(csv_path)
            assert len(prospects) == 2
            assert prospects[0]["first_name"] == "Alice"
            assert prospects[0]["segment"] == "open_to_work"
            assert prospects[1]["email"] == "bob@test.com"
        finally:
            os.unlink(csv_path)

    def test_skip_invalid_segment(self):
        """Rows with invalid segments are skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "email", "segment"])
            writer.writerow(["Alice", "Smith", "alice@test.com", "invalid_segment"])
            writer.writerow(["Bob", "Jones", "bob@test.com", "laid_off"])
            csv_path = f.name

        try:
            prospects = outreach.load_prospects(csv_path)
            assert len(prospects) == 1
            assert prospects[0]["first_name"] == "Bob"
        finally:
            os.unlink(csv_path)

    def test_skip_incomplete_rows(self):
        """Rows with missing fields are skipped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "email", "segment"])
            writer.writerow(["Alice", "", "alice@test.com", "open_to_work"])
            writer.writerow(["Bob", "Jones", "bob@test.com", "laid_off"])
            csv_path = f.name

        try:
            prospects = outreach.load_prospects(csv_path)
            assert len(prospects) == 1
        finally:
            os.unlink(csv_path)


# ============================================================
# Follow-up Logic Tests
# ============================================================

class TestFollowup:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self.conn = outreach.init_db(self.db_path)

    def teardown_method(self):
        self.conn.close()
        os.unlink(self.db_path)

    def test_finds_email2_candidates(self):
        """Finds prospects for Email 2 after 3+ days."""
        sent_at = (datetime.now() - timedelta(days=4)).isoformat()
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 1, sent_at, "sent"),
        )
        self.conn.commit()

        candidates = followup.get_followup_candidates(self.conn, 2, 3)
        assert len(candidates) == 1
        assert candidates[0]["email"] == "test@example.com"

    def test_excludes_replied(self):
        """Excludes prospects who have replied."""
        sent_at = (datetime.now() - timedelta(days=4)).isoformat()
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 1, sent_at, "replied"),
        )
        self.conn.commit()

        candidates = followup.get_followup_candidates(self.conn, 2, 3)
        assert len(candidates) == 0

    def test_excludes_already_sent(self):
        """Excludes prospects who already received the target email."""
        sent_at = (datetime.now() - timedelta(days=4)).isoformat()
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 1, sent_at, "sent"),
        )
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 2, datetime.now().isoformat(), "sent"),
        )
        self.conn.commit()

        candidates = followup.get_followup_candidates(self.conn, 2, 3)
        assert len(candidates) == 0

    def test_too_recent_not_included(self):
        """Prospects with recent Email 1 are not yet eligible."""
        sent_at = (datetime.now() - timedelta(days=1)).isoformat()
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 1, sent_at, "sent"),
        )
        self.conn.commit()

        candidates = followup.get_followup_candidates(self.conn, 2, 3)
        assert len(candidates) == 0


# ============================================================
# Monitor Logic Tests
# ============================================================

class TestMonitor:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self.conn = outreach.init_db(self.db_path)

    def teardown_method(self):
        self.conn.close()
        os.unlink(self.db_path)

    def test_get_known_prospects(self):
        """Retrieves known prospects from DB."""
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 1, datetime.now().isoformat(), "sent"),
        )
        self.conn.commit()

        prospects = monitor.get_known_prospects(self.conn)
        assert "test@example.com" in prospects
        assert prospects["test@example.com"]["first_name"] == "Test"

    def test_mark_as_replied(self):
        """Marking as replied updates all records for that email."""
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 1, datetime.now().isoformat(), "sent"),
        )
        self.conn.execute(
            "INSERT INTO outreach (email, first_name, last_name, segment, email_number, sent_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("test@example.com", "Test", "User", "open_to_work", 2, datetime.now().isoformat(), "sent"),
        )
        self.conn.commit()

        monitor.mark_as_replied(self.conn, "test@example.com")

        cursor = self.conn.execute(
            "SELECT status FROM outreach WHERE email = 'test@example.com'"
        )
        statuses = [row[0] for row in cursor.fetchall()]
        assert all(s == "replied" for s in statuses)

    def test_generate_response_interested(self):
        """Generates appropriate response for interested replies."""
        prospect = {"first_name": "Alice", "last_name": "Smith", "email": "alice@test.com", "segment": "open_to_work"}
        draft = monitor.generate_response_draft(prospect, "Yes, I'm interested! Tell me more.")
        assert "Alice" in draft
        assert "15-minute" in draft or "call" in draft.lower()

    def test_generate_response_pricing(self):
        """Generates pricing response for cost questions."""
        prospect = {"first_name": "Bob", "last_name": "Jones", "email": "bob@test.com", "segment": "mid_career"}
        draft = monitor.generate_response_draft(prospect, "How much does this cost?")
        assert "Bob" in draft
        assert "$" in draft

    def test_generate_response_unsubscribe(self):
        """Generates unsubscribe response."""
        prospect = {"first_name": "Carol", "last_name": "White", "email": "carol@test.com", "segment": "laid_off"}
        draft = monitor.generate_response_draft(prospect, "Please stop emailing me. Unsubscribe.")
        assert "Carol" in draft
        assert "removed" in draft.lower()

    def test_generate_response_generic(self):
        """Generates generic response for unclear replies."""
        prospect = {"first_name": "Dan", "last_name": "Brown", "email": "dan@test.com", "segment": "recent_grad"}
        draft = monitor.generate_response_draft(prospect, "Thanks for reaching out.")
        assert "Dan" in draft


# ============================================================
# Email Sending Tests (mocked)
# ============================================================

class TestEmailSending:
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        """send_email returns True on successful send."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        result = outreach.send_email(
            "smtp.test.com", 587, "user@test.com", "password",
            "to@test.com", "Test Subject", "<p>Test</p>",
        )
        assert result is True

    def test_send_email_dry_run(self):
        """Dry run mode doesn't attempt to connect."""
        result = outreach.send_email(
            "smtp.test.com", 587, "user@test.com", "password",
            "to@test.com", "Test Subject", "<p>Test</p>",
            dry_run=True,
        )
        assert result is True

    @patch("smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp):
        """send_email returns False on SMTP error."""
        mock_smtp.return_value.__enter__ = MagicMock(
            side_effect=smtplib.SMTPException("Connection failed")
        )
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        result = outreach.send_email(
            "smtp.test.com", 587, "user@test.com", "password",
            "to@test.com", "Test Subject", "<p>Test</p>",
        )
        assert result is False


# ============================================================
# Integration Test: Full outreach dry run
# ============================================================

class TestIntegration:
    def test_outreach_dry_run(self):
        """Full outreach flow works in dry-run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_prospects.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["first_name", "last_name", "email", "segment"])
                writer.writerow(["Alice", "Smith", "alice@test.com", "open_to_work"])
                writer.writerow(["Bob", "Jones", "bob@test.com", "career_changer"])

            db_path = os.path.join(tmpdir, "test.db")
            conn = outreach.init_db(db_path)

            prospects = outreach.load_prospects(csv_path)
            assert len(prospects) == 2

            for prospect in prospects:
                template = get_template(prospect["segment"], 1)
                subject = template["subject"].format(first_name=prospect["first_name"])
                body = template["body"].format(first_name=prospect["first_name"])

                result = outreach.send_email(
                    "smtp.test.com", 587, "user@test.com", "pass",
                    prospect["email"], subject, body, dry_run=True,
                )
                assert result is True

                outreach.record_send(
                    conn, prospect["email"], prospect["first_name"],
                    prospect["last_name"], prospect["segment"], 1,
                )

            count = outreach.get_today_send_count(conn)
            assert count == 2

            assert outreach.already_sent(conn, "alice@test.com", 1) is True
            assert outreach.already_sent(conn, "alice@test.com", 2) is False

            conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
