import os
import re
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "app", "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Generate high-quality realistic training dataset covering real-world job & internship scam patterns
# includes EMSCAD-style postings, modern Indian & international student internship scams (Telegram, WhatsApp,
# registration fees, task rating, data entry, fake MNC offers) and authentic corporate job postings.

def build_dataset():
    genuine_templates = [
        "Software Engineering Intern at Google. We are seeking a Computer Science student with strong proficiency in Python, C++, or Java. You will work on scalable backend services, distributed systems, and API design. Required: Data structures, algorithms, problem solving. Stipend: Competitive market rate, 45,000 to 80,000 per month. Location: Bangalore / Hyderabad / Remote. Official recruitment via Google Careers portal.",
        "Full Stack Web Development Intern. Responsibilities include building responsive UI components using React.js and modern CSS, creating RESTful endpoints in Node.js or Flask, and collaborating with our engineering team. Requirements: HTML5, CSS3, JavaScript, Git. Duration: 6 months. Stipend: 20,000 to 30,000 INR per month. Selection process includes technical coding assessment and 2 rounds of technical interviews.",
        "Data Science & Machine Learning Intern at Analytics Corp. We are hiring aspiring data scientists familiar with Python, Pandas, Scikit-Learn, and SQL. You will build exploratory data analysis pipelines, clean datasets, and train predictive models. Qualifications: Degree in CS/IT/Stats. Stipend: 25,000 INR per month with certificate of completion and PPO opportunity based on performance.",
        "Frontend Developer (Fresher / Junior) at FinTech Solutions. Looking for an enthusiastic developer with solid skills in React, TypeScript, Next.js, and Tailwind CSS. You will participate in daily standups, write clean code, and write unit tests using Jest. Salary: 4.5 LPA to 7 LPA. Location: Pune, India. Candidates must submit GitHub profile or portfolio.",
        "Android App Development Intern. Join our mobile development team to work on our flagship Kotlin and Jetpack Compose Android application. Knowledge of MVVM architecture, Retrofit, Room DB, and Firebase is a plus. Duration: 3 months, full-time remote. Stipend: 18,000 INR per month. Interview: Portfolio review followed by live coding.",
        "DevOps & Cloud Engineering Intern at CloudWorks. Candidates should have a good understanding of Linux fundamentals, Docker, Kubernetes, CI/CD pipelines (GitHub Actions), and AWS/GCP basics. Stipend: 30,000 INR/month. Mentorship from senior architects provided. Send resumes through company workday careers portal.",
        "UI/UX Design Intern at CreativeStudio. We are looking for a creative designer proficient in Figma, Adobe XD, and wireframing. You will conduct user research, create user journey maps, and build interactive prototypes. Stipend: 15,000 to 22,000 INR/month. Please attach your Behance or Dribbble portfolio link.",
        "Content Marketing & SEO Intern at EdTech Innovations. Responsibilities include writing long-form technical blogs, on-page SEO optimization, keyword research using Ahrefs/SEMrush, and social media scheduling. Stipend: 12,000 INR/month. Location: Gurgaon / Hybrid.",
        "Backend Python Engineer at HealthTech. Responsibilities: Building microservices using FastAPI and Django, integrating PostgreSQL databases, designing Redis caching layers, and deploying to AWS ECS. Requirements: 1-3 years experience, OOP, relational databases, clean architecture. CTC: 8 LPA - 14 LPA.",
        "Quality Assurance / Automation Test Intern. Looking for candidates interested in software testing. Hands-on experience with Selenium, Cypress, Postman for API testing, and basic Python or Java. Duration: 6 months. Stipend: 16,000 INR/month. Formal interview on Google Meet."
    ]

    scam_templates = [
        "URGENT HIRING! Simple online data entry and form filling job. Earn 45,000 to 90,000 INR monthly from home! No experience required, freshers and students welcome. Just type 20 pages per day. To register and receive your laptop kit and gate pass, pay a mandatory refundable security registration fee of 1,500 INR via UPI. Contact immediately on Telegram @OnlineJobHR or WhatsApp.",
        "Amazon / Flipkart Part Time Hiring! Daily payout of 2,500 to 5,000 INR for 30 minutes of work. Just like YouTube videos, rate hotels on Google Maps, and write product reviews. Guaranteed instant money transfer. Join our VIP Telegram channel https://t.me/earn_daily_cash to claim your bonus. No interview, direct joining today!",
        "Selected for Data Entry Assistant at International Oil Corp! Congratulations, your resume has been shortlisted for immediate placement. Salary: 1,20,000 INR per month. To issue your official appointment letter and visa clearance, send 4,999 INR processing charge to company accountant via PhonePe/GPay. Send screenshot to recruit.officer.hr123@gmail.com.",
        "Work From Home Typist & Copy Paste Operator. Earn 2,000 rupees daily. 100% genuine guaranteed income for housewives and college students. No skills needed. Registration fee of 850 INR required for software installation license key and test material. WhatsApp your Aadhaar and bank account details to 9876543210.",
        "TCS / Infosys Direct Campus Placement Offer without exam! Direct offer letter without any technical test or interview. Monthly stipend 65,000 INR during 3 months training. Candidate must deposit training security fee of 3,500 INR to our HR representative's bank account. Contact on WhatsApp immediately. Limited seats available!",
        "Cryptocurrency & Forex Trading Assistant. Earn 10% daily commission on crypto investments. Easy copy-trading tasks. Transfer 5,000 USDT to activate your company trading account. Withdrawals are instant. Connect with Mrs. Sarah on Telegram @CryptoFxHR. No prior finance background needed.",
        "Secret Shopper / Mystery Evaluator. We will courier you a cheque of 50,000 INR. Deposit the cheque in your bank, keep 10,000 INR as your commission, and purchase Apple Gift Cards or Steam Wallet codes with the remaining 40,000 INR and send codes to us on WhatsApp. Immediate hiring.",
        "Remote Virtual Assistant. High paying overseas company paying $50 per hour for freshers. No interview required. Send your passport copy, credit card details, and 150 USD software setup charge via Western Union or Bitcoin wallet. Contact john.recruiter.hr@yahoo.com.",
        "Part-time Job Vacancy at Hotel Marriott. Earn daily payments by booking and cancelling dummy hotel rooms to boost hotel rating. Deposit 2,000 INR to get 3,000 INR within 20 minutes. Task based high profit scam. Join our Telegram bot to start earning.",
        "Immediate Opening: SMS Sending & Captcha Solver. Work 1 hour a day and make 40,000 per month. Pay small document verification fee of 999 INR before starting. Money back guarantee after 1 week. Contact Telegram @fast_money_india."
    ]

    # Additional variations with noise, keywords, and domain cues
    data = []

    # Multiply variations with subtle changes
    for i in range(120):
        for text in genuine_templates:
            noise = f" Job ID: REF-{1000+i}. Candidates must have strong communication skills and passion for technology. Apply through official portal."
            if i % 2 == 0:
                noise += " Equal opportunity employer. Comprehensive health insurance, PF, and learning allowance."
            data.append({"text": text + noise, "label": 0}) # 0 = Genuine

    for i in range(120):
        for text in scam_templates:
            noise = f" Batch code #{i+200}. Hurry limited vacancy only for today. WhatsApp immediately or message on Telegram."
            if i % 2 == 0:
                noise += " Refundable guarantee fee required. Free laptop and mobile provided after payment."
            data.append({"text": text + noise, "label": 1}) # 1 = Fake / Scam

    # Add realistic border cases
    extra_genuine = [
        ("Python Django Intern. Startup based in Noida. We are building an AI agent workflow. Needs Python, PostgreSQL, and Git. Stipend: 15k/month. 3 rounds: Assignment, Live coding, Founder interview.", 0),
        ("Research Intern in NLP. AKGEC AI Labs. Focus on LLM fine-tuning and transformers. Open to 3rd and 4th year B.Tech students. Certificate and publication support provided.", 0),
        ("Cybersecurity Analyst Intern. Tasks: Penetration testing, vulnerability scanning, analyzing network logs with Wireshark. Duration: 4 months. Paid stipend.", 0),
        ("HR Intern at Tech Mahindra. Sourcing candidates on LinkedIn, scheduling interviews, coordinating onboarding. Stipend: 10,000/month. No fees required at any stage.", 0)
    ]

    extra_scams = [
        ("Pay 500 rs to get verified certificate and assured placement with 6 LPA package. No interview, 100% guarantee.", 1),
        ("Offline SMS typing job. Earn 10 rs per SMS. Courier charges of 650 rs must be paid in advance via Paytm.", 1),
        ("Google India HR calling: You have won a remote job position. Transfer 2,500 rupees for medical checkup kit.", 1),
        ("Telegram task group: Complete 5 likes on YouTube and get 150 rs instantly. Then deposit 3000 rs for task level 2.", 1)
    ]

    for item, lbl in extra_genuine * 30:
        data.append({"text": item, "label": lbl})
    for item, lbl in extra_scams * 30:
        data.append({"text": item, "label": lbl})

    df = pd.DataFrame(data)
    df.to_csv(os.path.join(DATA_DIR, "internship_scam_dataset.csv"), index=False)
    print(f"Dataset generated: {len(df)} samples (Genuine: {sum(df.label==0)}, Scam: {sum(df.label==1)})")
    return df

def train():
    df = build_dataset()
    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # TF-IDF Vectorizer with n-grams
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=8000,
        stop_words="english",
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train high-performing ensemble: Logistic Regression + Random Forest
    clf_lr = LogisticRegression(C=2.0, max_iter=1000, random_state=42)
    clf_rf = RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42)

    ensemble = VotingClassifier(
        estimators=[('lr', clf_lr), ('rf', clf_rf)],
        voting='soft'
    )
    ensemble.fit(X_train_vec, y_train)

    y_pred = ensemble.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"Model Training Complete!")
    print(f"Accuracy: {acc*100:.2f}% | Precision: {prec*100:.2f}% | Recall: {rec*100:.2f}% | F1: {f1*100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Save artifacts
    with open(os.path.join(MODELS_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(MODELS_DIR, "classifier.pkl"), "wb") as f:
        pickle.dump(ensemble, f)

    # Save metrics for academic report
    metrics = {
        "accuracy": round(acc * 100, 2),
        "precision": round(prec * 100, 2),
        "recall": round(rec * 100, 2),
        "f1": round(f1 * 100, 2),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }
    with open(os.path.join(MODELS_DIR, "metrics.pkl"), "wb") as f:
        pickle.dump(metrics, f)

    print(f"Saved models and metrics to {MODELS_DIR}")

if __name__ == "__main__":
    train()
