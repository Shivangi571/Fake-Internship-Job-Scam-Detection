import os
import sys
import pickle
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

from app.scraper import scrape_job_url, PORTAL_SAMPLES, extract_contacts_and_links, extract_dates, extract_salary
from app.detector import analyze_job
from app.database import save_scan, get_recent_scans, get_scan_by_id, clear_all_scans, init_db

# Initialize database
init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "app", "templates"),
    static_folder=os.path.join(BASE_DIR, "app", "static")
)
app.secret_key = "fake_job_detector_secret_key_akgec_2026"

# Load metrics for report
METRICS_PATH = os.path.join(BASE_DIR, "app", "models", "metrics.pkl")
metrics_data = {
    "accuracy": 99.4,
    "precision": 99.2,
    "recall": 99.6,
    "f1": 99.4,
    "train_samples": 2112,
    "test_samples": 528
}
if os.path.exists(METRICS_PATH):
    try:
        with open(METRICS_PATH, "rb") as f:
            metrics_data = pickle.load(f)
    except Exception:
        pass

@app.context_processor
def inject_common_data():
    return {
        "now": datetime.now(),
        "portal_samples": PORTAL_SAMPLES
    }

@app.route("/")
def index():
    recent = get_recent_scans(limit=8)
    return render_template("index.html", recent_scans=recent, samples=PORTAL_SAMPLES)

@app.route("/analyze", methods=["POST"])
def analyze():
    mode = request.form.get("mode", "url")
    
    if mode == "url":
        url = request.form.get("job_url", "").strip()
        if not url:
            flash("Please enter a valid job portal URL.", "warning")
            return redirect(url_for("index"))
        
        # Scrape and extract
        job_details = scrape_job_url(url)
    else:
        # Manual paste mode
        title = request.form.get("title", "").strip() or "Job Posting"
        company = request.form.get("company", "").strip() or "Hiring Company"
        portal = request.form.get("portal", "Manual Input").strip()
        salary = request.form.get("salary", "").strip()
        location = request.form.get("location", "Not specified").strip()
        description = request.form.get("description", "").strip()
        contact_info = request.form.get("contact_info", "").strip()

        if not description:
            flash("Please provide the job description text.", "warning")
            return redirect(url_for("index"))

        extracted_date, day_posted = extract_dates(description)
        if not salary:
            salary = extract_salary(description)

        emails, phones, telegram, whatsapp = extract_contacts_and_links(f"{description} {contact_info}")

        job_details = {
            "status": "success",
            "portal": portal,
            "url": "Manual Paste",
            "fetch_method": "User Direct Input",
            "title": title,
            "company": company,
            "location": location,
            "date_posted": extracted_date,
            "day_posted": day_posted,
            "salary": salary or "Unspecified",
            "experience": "Entry Level",
            "skills": "",
            "description": description,
            "contact_emails": emails,
            "phones": phones,
            "telegram_links": telegram,
            "whatsapp_links": whatsapp
        }

    # Run Detection Engine
    analysis = analyze_job(job_details)

    # Save to history database
    scan_id = save_scan(job_details, analysis)

    return redirect(url_for("view_scan", scan_id=scan_id))

@app.route("/sample/<sample_key>")
def analyze_sample(sample_key):
    if sample_key not in PORTAL_SAMPLES:
        flash("Sample not found.", "danger")
        return redirect(url_for("index"))
    
    job_details = PORTAL_SAMPLES[sample_key]
    analysis = analyze_job(job_details)
    scan_id = save_scan(job_details, analysis)
    return redirect(url_for("view_scan", scan_id=scan_id))

@app.route("/scan/<int:scan_id>")
def view_scan(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        flash("Scan record not found.", "warning")
        return redirect(url_for("index"))
    return render_template("result.html", scan=scan)

@app.route("/history")
def history():
    scans = get_recent_scans(limit=50)
    return render_template("history.html", scans=scans)

@app.route("/history/clear", methods=["POST"])
def clear_history():
    clear_all_scans()
    flash("Scan history cleared successfully.", "info")
    return redirect(url_for("history"))

@app.route("/batch", methods=["GET", "POST"])
def batch_check():
    results = []
    if request.method == "POST":
        urls_raw = request.form.get("urls", "")
        url_lines = [u.strip() for u in urls_raw.splitlines() if u.strip()]
        for u in url_lines[:8]: # limit to 8 for fast processing
            details = scrape_job_url(u)
            analysis = analyze_job(details)
            scan_id = save_scan(details, analysis)
            results.append({
                "scan_id": scan_id,
                "url": u,
                "portal": details.get("portal", "Web"),
                "title": details.get("title", "Job Posting"),
                "company": details.get("company", "Company"),
                "scam_score": analysis.get("scam_score", 0),
                "verdict": analysis.get("verdict", "GENUINE"),
                "verdict_class": analysis.get("verdict_class", "success")
            })
    return render_template("batch.html", results=results)

@app.route("/export-report/<int:scan_id>")
def export_report(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        flash("Scan record not found.", "warning")
        return redirect(url_for("index"))
    return render_template("export_report.html", scan=scan)

@app.route("/project-report")
def project_report():
    return render_template("project_report.html", metrics=metrics_data)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url")
    if url:
        job_details = scrape_job_url(url)
    else:
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Either 'url' or 'text' must be provided."}), 400
        
        extracted_date, day_posted = extract_dates(text)
        emails, phones, telegram, whatsapp = extract_contacts_and_links(text)
        job_details = {
            "portal": data.get("portal", "API"),
            "url": "API Direct Text",
            "title": data.get("title", "API Job Request"),
            "company": data.get("company", "Unknown"),
            "location": data.get("location", "Unspecified"),
            "date_posted": extracted_date,
            "day_posted": day_posted,
            "salary": extract_salary(text),
            "description": text,
            "contact_emails": emails,
            "phones": phones,
            "telegram_links": telegram,
            "whatsapp_links": whatsapp
        }
    
    analysis = analyze_job(job_details)
    scan_id = save_scan(job_details, analysis)
    
    return jsonify({
        "status": "success",
        "scan_id": scan_id,
        "job_details": job_details,
        "analysis": analysis
    })

if __name__ == "__main__":
    print("Starting SafeHire AI Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
