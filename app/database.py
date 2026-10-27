import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "scans.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            portal TEXT,
            url TEXT,
            salary TEXT,
            date_posted TEXT,
            day_posted TEXT,
            scam_score REAL,
            trust_score REAL,
            verdict TEXT,
            verdict_class TEXT,
            raw_details TEXT,
            analysis_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_scan(job_details: dict, analysis: dict) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (
            title, company, portal, url, salary, date_posted, day_posted,
            scam_score, trust_score, verdict, verdict_class,
            raw_details, analysis_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_details.get("title", "Untitled Job"),
        job_details.get("company", "Unknown"),
        job_details.get("portal", "Web"),
        job_details.get("url", ""),
        job_details.get("salary", "Not specified"),
        job_details.get("date_posted", datetime.now().strftime("%d %b %Y")),
        job_details.get("day_posted", datetime.now().strftime("%A")),
        analysis.get("scam_score", 0.0),
        analysis.get("trust_score", 100.0),
        analysis.get("verdict", "GENUINE"),
        analysis.get("verdict_class", "success"),
        json.dumps(job_details),
        json.dumps(analysis),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id

def get_recent_scans(limit=20):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    scans = []
    for r in rows:
        scans.append({
            "id": r["id"],
            "title": r["title"],
            "company": r["company"],
            "portal": r["portal"],
            "url": r["url"],
            "salary": r["salary"],
            "date_posted": r["date_posted"],
            "day_posted": r["day_posted"],
            "scam_score": r["scam_score"],
            "trust_score": r["trust_score"],
            "verdict": r["verdict"],
            "verdict_class": r["verdict_class"],
            "created_at": r["created_at"]
        })
    conn.close()
    return scans

def get_scan_by_id(scan_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    scan = {
        "id": row["id"],
        "title": row["title"],
        "company": row["company"],
        "portal": row["portal"],
        "url": row["url"],
        "salary": row["salary"],
        "date_posted": row["date_posted"],
        "day_posted": row["day_posted"],
        "scam_score": row["scam_score"],
        "trust_score": row["trust_score"],
        "verdict": row["verdict"],
        "verdict_class": row["verdict_class"],
        "created_at": row["created_at"],
        "job_details": json.loads(row["raw_details"]),
        "analysis": json.loads(row["analysis_json"])
    }
    conn.close()
    return scan

def clear_all_scans():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans")
    conn.commit()
    conn.close()

init_db()
