# SafeHire AI &mdash; Fake Internship & Job Scam Detection System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20NLP-orange.svg)](https://scikit-learn.org/)
[![College](https://img.shields.io/badge/AKGEC-Ghaziabad%20%7C%20AKTU-purple.svg)](https://www.akgec.ac.in)

> **B.Tech Computer Science & Engineering Final Year Project**  
> **Institution:** Ajay Kumar Garg Engineering College (AKGEC), Ghaziabad  
> **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow  
> **Supervisor:** Dr. Anuj Kumar, Assistant Professor, Department of CSE  

---

## 📌 Project Overview

**SafeHire AI** is an advanced cyber-safety platform designed to protect students and fresh graduates from fraudulent internship postings and employment scams. The platform accepts URLs from popular recruitment platforms (**Internshala, LinkedIn, Indeed, Foundit, Wellfound**, and direct career pages) or raw job descriptions.

It extracts key posting metadata—such as **posting date, day of week, salary/stipend, company name, location, and communication handles**—and conducts deep risk analysis using an ensemble Machine Learning model coupled with a deterministic heuristic red-flag rule engine.

---

## 🚀 Key Features

1. **Multi-Portal Web Scraper & Extractor**:
   - Supports **Internshala**, **LinkedIn**, **Indeed**, **Foundit (Monster)**, **Wellfound (AngelList)**, and generic job boards.
   - Extracts JSON-LD `schema.org/JobPosting` structured data, OpenGraph tags, and DOM elements.
   - Automatically parses:
     - **Role Title & Company Name**
     - **Posting Date & Exact Day of Week** (e.g. *24 Oct 2026, Saturday*)
     - **Salary & Stipend Range** (e.g. *₹25,000 / month*, *4.5 - 7 LPA*, *Unpaid*)
     - **Full Job Description & Eligibility Criteria**
     - **Contact Handles**: Emails, Phone Numbers, WhatsApp numbers, Telegram links (`t.me/...`, `@handle`).
   - Anti-bot fallback protection with graceful manual paste fallback and pre-loaded test fixtures.

2. **Hybrid Scam Detection Engine**:
   - **Machine Learning Layer**: TF-IDF n-gram vectorizer (unigrams, bigrams, trigrams) combined with an ensemble soft-voting classifier (**Random Forest + Logistic Regression**) trained on 2,600+ real-world employment postings.
   - **Rule-Based Heuristic Layer**:
     - **Financial Extortion**: Registration charges, refundable security deposits, laptop fees, gate pass charges, crypto/gift card payments.
     - **Dubious Channels**: Telegram-only recruiters, WhatsApp interview groups, corporate recruiters using personal `@gmail.com` or `@yahoo.com` emails.
     - **Task / Rating Scams**: YouTube video likes, Google Maps hotel rating tasks, SMS sending, data entry book typing.
     - **Unrealistic Claims**: Exorbitant daily payouts for minimal work, direct appointment letters issued without interview or technical test.
   - **Explainable AI (XAI)**:
     - Composite Scam Probability Score (0% to 100%)
     - Trust Index
     - 4 Risk Radar Dimensions: *Financial Risk, Channel Risk, Task Fraud Risk, Urgency Anomaly*
     - Flagged Keywords with exact contextual excerpts.
     - Positive Genuine Hiring Signals (e.g., technical coding assessment, Git repo, relational databases).

3. **High-Grade UI & Interactive Dashboards**:
   - Modern, responsive theme with SVG circular risk gauges and color-coded status badges.
   - **1-Click Showcase Samples**: Pre-loaded test cases for Internshala, LinkedIn, Indeed, Foundit, and Wellfound (both Genuine and Scam).
   - **Batch URL Checker**: Check up to 8 job postings in bulk.
   - **Persistent SQLite Audit History**: Search, review, and clear past scan records.
   - **Formal Security Audit Certificate**: Printable / export-ready PDF report for scanned positions.

4. **Academic Project Report Viewer**:
   - Formatted specifically according to the **AKGEC B.Tech CSE Department Report Guidelines** (Title Page, Certificate, Declaration, Abstract, Introduction, System Design, Model Comparison Table, Hardware/Software Implementation, Results, References).

---

## 📁 Directory Structure

```
fake_job_detector/
├── app/
│   ├── __init__.py           # Package initializer
│   ├── scraper.py            # Intelligent scraper for 5 portals + regex extractors
│   ├── detector.py           # Hybrid ML + Heuristic scam detection engine
│   ├── database.py           # SQLite persistence layer for scan audits
│   ├── models/               # Serialized ML models & metrics
│   │   ├── classifier.pkl
│   │   ├── vectorizer.pkl
│   │   └── metrics.pkl
│   ├── static/
│   │   └── css/
│   │       └── custom.css    # Custom UI styling, gauges, risk bars
│   └── templates/
│       ├── base.html         # Base layout with navigation and AKGEC footer
│       ├── index.html        # Main dashboard with scanner tabs & samples
│       ├── result.html       # Comprehensive audit report with gauge & XAI
│       ├── history.html      # Persistent scan audit log
│       ├── batch.html        # Multi-URL batch inspector
│       ├── export_report.html# Printable official audit certificate
│       └── project_report.html# AKGEC B.Tech CSE Project Report
├── data/
│   ├── scans.db              # SQLite database
│   └── internship_scam_dataset.csv
├── run.py                    # Flask application entry point
├── train_model.py            # Model training & evaluation pipeline
├── test_app.py               # Automated integration test suite
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start Instructions

### 1. Requirements
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Re-train the Model
```bash
python train_model.py
```
*Trained metrics: 99.4% Accuracy, 99.2% Precision, 99.6% Recall, 99.4% F1-Score.*

### 4. Run the Application
```bash
python run.py
```
Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

### 5. Run Automated System Tests
```bash
python test_app.py
```

---

## 🌐 REST API Usage

You can also send programmatic requests to SafeHire AI:

### Analyze Text / Job Description:
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Online Typing Assistant",
    "text": "Earn 50000 daily typing books. Pay refundable security deposit 1200 via UPI and join Telegram."
  }'
```

**Sample JSON Response:**
```json
{
  "status": "success",
  "scan_id": 1,
  "analysis": {
    "scam_score": 85.0,
    "trust_score": 15.0,
    "verdict": "LIKELY FAKE / SCAM",
    "verdict_class": "danger",
    "dimension_scores": {
      "financial_risk": 60,
      "communication_risk": 50,
      "task_scam_risk": 40,
      "urgency_risk": 45
    }
  }
}
```

---

## 🎓 Academic Citations & Context
This project was designed in accordance with the project syllabus of **Ajay Kumar Garg Engineering College, Ghaziabad** affiliated with **Dr. A.P.J. Abdul Kalam Technical University (AKTU)**.
