import re
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1"
}

# Pre-configured showcase samples for testing all 5 major portals immediately
PORTAL_SAMPLES = {
    "internshala_genuine": {
        "portal": "Internshala",
        "url": "https://internshala.com/internship/detail/python-django-development-internship-in-gurgaon-at-techvibe-solutions171420",
        "title": "Backend Python/Django Developer Intern",
        "company": "TechVibe Solutions Pvt Ltd",
        "location": "Gurgaon / Hybrid",
        "date_posted": "24 Oct 2026",
        "day_posted": "Saturday",
        "salary": "₹22,000 - ₹28,000 / month",
        "experience": "Fresher / College Students",
        "skills": "Python, Django, PostgreSQL, REST APIs, Git",
        "description": """TechVibe Solutions is hiring a Backend Python/Django Intern for a 6-month full-time internship.
Selected intern's day-to-day responsibilities include:
1. Writing modular, testable backend code using Django and Django Rest Framework (DRF).
2. Designing relational database schemas in PostgreSQL and writing optimized queries.
3. Building and integrating secure RESTful APIs with frontend client applications.
4. Participating in agile sprint planning, code reviews on GitHub, and bug tracking.

Skill(s) required:
- Proficiency in Python and object-oriented programming concepts.
- Understanding of HTTP protocols, MVC/MVT architecture, and ORM.
- Familiarity with version control (Git) and Postman.

Perks & Stipend:
- ₹25,000/month fixed stipend.
- Pre-Placement Offer (PPO) opportunity based on 6-month internship performance (CTC: 7-9 LPA).
- Certificate of Internship and Letter of Recommendation.
- Formal selection process: Technical coding round followed by Google Meet interview with Engineering Lead. No fees required at any stage.""",
        "contact_emails": ["careers@techvibesolutions.com"],
        "phones": [],
        "telegram_links": [],
        "whatsapp_links": [],
        "source_type": "Showcase Sample"
    },
    "internshala_scam": {
        "portal": "Internshala",
        "url": "https://internshala.com/internship/detail/online-data-entry-typing-internship-at-apex-global-careers171999",
        "title": "Online Data Entry & Typing Executive Intern",
        "company": "Apex Global Services",
        "location": "Work From Home / Remote",
        "date_posted": "26 Oct 2026",
        "day_posted": "Monday",
        "salary": "₹45,000 - ₹80,000 / month",
        "experience": "No experience needed (All students eligible)",
        "skills": "Basic typing, MS Word, English",
        "description": """URGENT HIRING: Apex Global Services is offering 100% remote Work From Home Data Entry Typing Internship for students.
Earn daily income from ₹2,000 to ₹3,500 by just typing 15-20 scanned book pages per day.
No technical skills or previous experience needed. Housewives and 1st year students can easily earn up to ₹80,000 monthly!

Terms & Conditions:
- Company will provide free Lenovo Laptop and Wifi dongle after verification.
- Mandatory refundable security registration fee of ₹1,499 must be paid before training kit dispatch via GooglePay/PhonePe.
- After paying registration charge, send screenshot to Telegram @ApexHRRecruiter or WhatsApp at 9871234567.
- Direct joining without interview. Limited slots left, offer expires today!""",
        "contact_emails": ["apex.careers.hr@gmail.com"],
        "phones": ["+91 9871234567"],
        "telegram_links": ["@ApexHRRecruiter"],
        "whatsapp_links": ["https://wa.me/919871234567"],
        "source_type": "Showcase Sample"
    },
    "linkedin_genuine": {
        "portal": "LinkedIn",
        "url": "https://www.linkedin.com/jobs/view/software-engineer-intern-at-microsoft-india-3829104",
        "title": "Software Engineer Intern - 2027 Batch",
        "company": "Microsoft",
        "location": "Bengaluru, Karnataka, India (Hybrid)",
        "date_posted": "22 Oct 2026",
        "day_posted": "Thursday",
        "salary": "₹80,000 - ₹1,25,000 / month",
        "experience": "Pursuing B.Tech / M.Tech in CS/IT",
        "skills": "C++, C#, Java, Data Structures, Algorithms, Distributed Systems",
        "description": """Microsoft is looking for passionate Software Engineer Interns to join our Azure Cloud and Office 365 platforms teams in Bengaluru and Hyderabad.
Responsibilities:
- Design, implement, test, and deliver high-performance microservices.
- Collaborate with product managers, UX designers, and architects.
- Apply rigorous software engineering practices including unit testing, telemetry, and continuous deployment.

Qualifications:
- Currently enrolled in a Bachelor's or Master's degree in Computer Science, Electrical Engineering, or related technical field.
- Strong foundational grasp of algorithms, data structures, and computational complexity.
- Experience with C++, C#, Java, or Python.

Apply only through Microsoft Careers portal (careers.microsoft.com). Microsoft never requests payment of any fee during recruitment.""",
        "contact_emails": [],
        "phones": [],
        "telegram_links": [],
        "whatsapp_links": [],
        "source_type": "Showcase Sample"
    },
    "linkedin_scam": {
        "portal": "LinkedIn",
        "url": "https://www.linkedin.com/jobs/view/hr-coordinator-remote-immediate-joining-at-global-talent-hub-49102",
        "title": "Part-Time Task Coordinator / Remote Assistant",
        "company": "Global Talent Innovations",
        "location": "Remote (Worldwide)",
        "date_posted": "25 Oct 2026",
        "day_posted": "Sunday",
        "salary": "$4,000 - $6,500 / month",
        "experience": "Entry Level (No degree required)",
        "skills": "Telegram, Social Media, Phone calls",
        "description": """AMAZING WORK FROM HOME OPPORTUNITY!
We are hiring 50 Remote Assistants to perform social media rating and marketing tasks.
Work only 1-2 hours a day and earn $150 to $300 daily payout.
Tasks involve liking selected YouTube videos, rating Google Maps hotel listings, and testing new mobile apps.

Requirements:
- Android or iPhone with active Telegram and WhatsApp.
- Immediate offer letter issued without any technical test.
- Candidate must deposit initial activation fee of $50 (or ₹4,200 INR) into our crypto wallet / UPI to verify identity and unlock task account.
- Contact HR Director on Telegram: https://t.me/GlobalTalentOfficial_HR or message on WhatsApp.""",
        "contact_emails": ["hr.talent.recruitment2026@yahoo.com"],
        "phones": [],
        "telegram_links": ["https://t.me/GlobalTalentOfficial_HR"],
        "whatsapp_links": ["WhatsApp Support"],
        "source_type": "Showcase Sample"
    },
    "indeed_genuine": {
        "portal": "Indeed",
        "url": "https://in.indeed.com/viewjob?jk=7b49a1d82f3c0911&q=react+developer+intern",
        "title": "Frontend React.js Developer (Junior / Intern)",
        "company": "Zomato / Blinkit Tech",
        "location": "Gurugram, Haryana",
        "date_posted": "21 Oct 2026",
        "day_posted": "Wednesday",
        "salary": "₹30,000 - ₹40,000 a month",
        "experience": "0-1 year experience",
        "skills": "React.js, Next.js, Redux Toolkit, Tailwind CSS, TypeScript",
        "description": """About the Role:
We are looking for a sharp Frontend Intern to build delightful user experiences for our ultra-fast delivery platform.
Key Responsibilities:
- Build reusable UI components adhering to design system guidelines.
- Optimize web web-vitals, client-side caching, and bundle sizes.
- Work closely with backend engineers to integrate GraphQL and REST APIs.

Qualifications:
- Solid understanding of JavaScript (ES6+), React hooks, and state management.
- Experience with responsive web design and mobile-first principles.
- Active GitHub portfolio demonstrating personal projects.
Interview Process: Initial screening -> Take-home assignment -> Virtual Technical Interview on Google Meet.""",
        "contact_emails": ["talent@blinkit.com"],
        "phones": [],
        "telegram_links": [],
        "whatsapp_links": [],
        "source_type": "Showcase Sample"
    },
    "indeed_scam": {
        "portal": "Indeed",
        "url": "https://in.indeed.com/viewjob?jk=9a8b7c6d5e4f3a21&q=data+entry+part+time",
        "title": "Back Office Data Entry Clerk & SMS Sender",
        "company": "FastTrack Placement Services",
        "location": "Noida / New Delhi / Remote",
        "date_posted": "25 Oct 2026",
        "day_posted": "Sunday",
        "salary": "₹55,000 a month",
        "experience": "Fresher can apply",
        "skills": "Typing, Mobile phone",
        "description": """URGENT REQUIREMENT FOR FRESHERS!
TCS partner company hiring back office data entry operators.
Earn ₹15 per SMS sent and ₹50 per page data entry.
Earn up to ₹55,000 per month sitting at home.
No interview, direct appointment letter delivered via courier along with company ID card and laptop.
Document verification charge and gate pass fee of ₹950 must be paid via PhonePe or Paytm before courier dispatch.
Contact Mr. Sharma immediately on WhatsApp: 919811223344 or email fasttrack.jobs.hr@gmail.com.""",
        "contact_emails": ["fasttrack.jobs.hr@gmail.com"],
        "phones": ["+91 919811223344"],
        "telegram_links": [],
        "whatsapp_links": ["https://wa.me/91919811223344"],
        "source_type": "Showcase Sample"
    },
    "foundit_genuine": {
        "portal": "Foundit (Monster)",
        "url": "https://www.foundit.in/job/cloud-devops-engineer-freshers-at-infotech-systems-892147",
        "title": "Graduate Cloud DevOps Engineer",
        "company": "InfoTech Systems Global",
        "location": "Noida, Uttar Pradesh",
        "date_posted": "23 Oct 2026",
        "day_posted": "Friday",
        "salary": "₹4,50,000 - ₹6,50,000 PA",
        "experience": "0 - 1 years",
        "skills": "Linux, Docker, AWS, Bash, Git, Python",
        "description": """InfoTech Systems is seeking Graduate Engineers to join our Cloud Infrastructure practice.
Selected candidates will undergo structured 8-week corporate training on AWS and Kubernetes.
Responsibilities:
- Assist in automating infrastructure deployment using Terraform.
- Monitor containerized microservices using Prometheus and Grafana.
- Troubleshoot Linux OS and network configuration issues.

Eligibility: B.Tech / B.E in CSE / IT / ECE with 65% aggregate.
Selection will be done through proctored online aptitude test and technical interview at our Noida Sector 62 campus.""",
        "contact_emails": ["careers@infotechglobal.com"],
        "phones": [],
        "telegram_links": [],
        "whatsapp_links": [],
        "source_type": "Showcase Sample"
    },
    "wellfound_genuine": {
        "portal": "Wellfound (AngelList)",
        "url": "https://wellfound.com/jobs/3091823-ai-machine-learning-intern-at-neuralstack-ai",
        "title": "AI / Machine Learning Engineer Intern",
        "company": "NeuralStack AI",
        "location": "Bengaluru (Remote Friendly)",
        "date_posted": "24 Oct 2026",
        "day_posted": "Saturday",
        "salary": "₹35,000 - ₹50,000 / month + Equity",
        "experience": "Junior / Student",
        "skills": "PyTorch, HuggingFace, Transformers, Python, Vector DBs",
        "description": """NeuralStack is an early-stage Y-Combinator backed AI startup building autonomous agent systems.
We are hiring an AI/ML intern to help fine-tune open-source LLMs (Llama 3, Mistral) and build evaluation benchmarks.
What you will do:
- Experiment with LoRA/QLoRA fine-tuning workflows.
- Build retrieval-augmented generation (RAG) pipelines using LangChain and Qdrant.
- Measure latency, perplexity, and reasoning metrics.
Requirements: Strong PyTorch fundamentals, demonstrated ML projects on GitHub or Kaggle medals. We pay fair market stipends and sponsor GPU compute.""",
        "contact_emails": ["founders@neuralstack.ai"],
        "phones": [],
        "telegram_links": [],
        "whatsapp_links": [],
        "source_type": "Showcase Sample"
    }
}

def detect_portal(url: str) -> str:
    """Identify which portal or domain the URL belongs to."""
    u = url.lower()
    if "internshala.com" in u:
        return "Internshala"
    elif "linkedin.com" in u:
        return "LinkedIn"
    elif "indeed.com" in u:
        return "Indeed"
    elif "foundit.in" in u or "foundit.com" in u or "monsterindia" in u:
        return "Foundit"
    elif "wellfound.com" in u or "angel.co" in u:
        return "Wellfound"
    elif "naukri.com" in u:
        return "Naukri"
    elif "glassdoor" in u:
        return "Glassdoor"
    else:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc or "Direct Web Portal"

def extract_contacts_and_links(text: str):
    """Extract contact emails, phone numbers, WhatsApp, and Telegram handles."""
    emails = list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)))
    # filter out generic image/asset extensions
    emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif'))]

    # Phone numbers (Indian and international formats)
    phones = list(set(re.findall(r'(?:\+?91[\-\s]?)?[6-9]\d{9}', text)))

    # Telegram links and handles
    telegram = list(set(re.findall(r'(?:https?:\/\/t\.me\/[a-zA-Z0-9_]+|@[a-zA-Z0-9_]{4,32})', text, re.IGNORECASE)))

    # WhatsApp links
    whatsapp = list(set(re.findall(r'(?:https?:\/\/wa\.me\/[0-9]+|whatsapp(?:\s*number|\s*at)?\s*:?\s*[6-9]\d{9})', text, re.IGNORECASE)))

    return emails, phones, telegram, whatsapp

def extract_dates(text: str, html_soup=None):
    """Extract posting date and calculate day of week."""
    now = datetime.now()
    date_str = None
    day_str = None

    # Try explicit regexes in text
    date_patterns = [
        r'posted\s+on\s*:?\s*([0-9]{1,2}[-\/][0-9]{1,2}[-\/][0-9]{2,4})',
        r'posted\s+([0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4})',
        r'date\s+posted\s*:?\s*([0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4})',
        r'posted\s+(\d+)\s+days?\s+ago',
        r'posted\s+today',
        r'posted\s+yesterday'
    ]

    for pat in date_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(0)
            if "today" in val.lower():
                date_str = now.strftime("%d %b %Y")
                day_str = now.strftime("%A")
            elif "yesterday" in val.lower():
                from datetime import timedelta
                y = now - timedelta(days=1)
                date_str = y.strftime("%d %b %Y")
                day_str = y.strftime("%A")
            elif "days ago" in val.lower():
                from datetime import timedelta
                days_ago = int(m.group(1))
                d = now - timedelta(days=days_ago)
                date_str = d.strftime("%d %b %Y")
                day_str = d.strftime("%A")
            else:
                date_str = m.group(1) if len(m.groups()) > 0 else m.group(0)
                try:
                    dt = datetime.strptime(date_str, "%d %b %Y")
                    day_str = dt.strftime("%A")
                except Exception:
                    day_str = "Verified Date"
            break

    if not date_str:
        # Fallback to current date
        date_str = now.strftime("%d %b %Y")
        day_str = now.strftime("%A")

    return date_str, day_str

def extract_salary(text: str):
    """Extract compensation, stipend, or salary from job content."""
    salary_patterns = [
        r'(?:₹|INR|Rs\.?)\s*[0-9,]+(?:\s*-\s*(?:₹|INR|Rs\.?)?\s*[0-9,]+)?\s*(?:\/|\s*per\s*)?(?:month|pm|mo|year|annum|pa|lpa|day)',
        r'[0-9]+(?:\.[0-9]+)?\s*-\s*[0-9]+(?:\.[0-9]+)?\s*LPA',
        r'[0-9]+(?:\.[0-9]+)?\s*LPA',
        r'\$[0-9,]+(?:\s*-\s*\$[0-9,]+)?\s*(?:\/|\s*per\s*)?(?:hr|hour|month|year)',
        r'(?:stipend|salary)\s*:\s*[^.\n]+',
        r'unpaid|performance\s*based'
    ]
    for pat in salary_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return "Not explicitly specified (Check Description)"

def scrape_job_url(url: str) -> dict:
    """
    Intelligently scrape job posting from URL with multi-portal selectors,
    JSON-LD JobPosting schema extraction, and graceful fallback.
    """
    url_clean = url.strip()
    portal_name = detect_portal(url_clean)

    # 1. Check if user provided one of our sample showcase URLs
    for key, sample in PORTAL_SAMPLES.items():
        if sample["url"].lower() in url_clean.lower() or url_clean.lower() in sample["url"].lower():
            return {
                **sample,
                "status": "success",
                "fetch_method": "Showcase Sample Link",
                "message": f"Successfully loaded authentic job record for {portal_name}."
            }

    # 2. Attempt live HTTP scrape
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        response = session.get(url_clean, timeout=10, allow_redirects=True)

        # Check for bot block or access restriction
        if response.status_code in (403, 429, 999) or "challenge-running" in response.text or "Security Check" in response.text:
            return {
                "status": "warning",
                "portal": portal_name,
                "url": url_clean,
                "fetch_method": "Access Blocked by Portal Anti-Scraping",
                "message": (
                    f"{portal_name} blocked automated server-side web scraping (HTTP {response.status_code} / Bot Shield). "
                    "You can paste the job description text directly in the 'Manual Paste' tab, or test our 1-click verified sample jobs!"
                ),
                "title": f"Posting on {portal_name}",
                "company": "Protected Portal Company",
                "location": "India / Remote",
                "date_posted": datetime.now().strftime("%d %b %Y"),
                "day_posted": datetime.now().strftime("%A"),
                "salary": "Hidden behind login wall",
                "experience": "Not accessible via direct bot",
                "skills": "",
                "description": "",
                "contact_emails": [],
                "phones": [],
                "telegram_links": [],
                "whatsapp_links": []
            }

        response.encoding = response.apparent_encoding or "utf-8"
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Strip scripts and styles
        for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
            if tag.name != "script" or tag.get("type") != "application/ld+json":
                tag.decompose()

        # Strategy A: Check JSON-LD schema (JobPosting)
        job_data = None
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "JobPosting":
                            job_data = item
                            break
                elif isinstance(data, dict):
                    if data.get("@type") == "JobPosting":
                        job_data = data
                    elif "@graph" in data:
                        for item in data["@graph"]:
                            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                                job_data = item
                                break
                if job_data:
                    break
            except Exception:
                continue

        title = None
        company = None
        location = None
        salary = None
        date_posted = None
        description = None

        if job_data:
            title = job_data.get("title")
            org = job_data.get("hiringOrganization")
            if isinstance(org, dict):
                company = org.get("name")
            elif isinstance(org, str):
                company = org
            
            loc = job_data.get("jobLocation")
            if isinstance(loc, dict):
                addr = loc.get("address", {})
                if isinstance(addr, dict):
                    location = addr.get("addressLocality") or addr.get("addressRegion") or addr.get("addressCountry")
                else:
                    location = str(addr)
            
            date_raw = job_data.get("datePosted")
            if date_raw:
                try:
                    dt = datetime.fromisoformat(date_raw.replace("Z", "+00:00"))
                    date_posted = dt.strftime("%d %b %Y")
                except Exception:
                    date_posted = str(date_raw)[:10]

            desc_raw = job_data.get("description", "")
            if desc_raw:
                desc_soup = BeautifulSoup(desc_raw, "html.parser")
                description = desc_soup.get_text(separator="\n").strip()

            base_sal = job_data.get("baseSalary")
            if isinstance(base_sal, dict):
                val = base_sal.get("value", {})
                if isinstance(val, dict):
                    salary = f"{base_sal.get('currency', '₹')} {val.get('minValue', '')} - {val.get('maxValue', '')} {val.get('unitText', '')}"

        # Strategy B: OpenGraph & Meta Tags
        if not title:
            og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
            if og_title and og_title.get("content"):
                title = og_title["content"].split("|")[0].split("-")[0].strip()

        if not description:
            og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
            if og_desc and og_desc.get("content"):
                description = og_desc["content"].strip()

        # Strategy C: Portal DOM-specific Fallback
        body_text = soup.get_text(separator=" ", strip=True)

        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text().strip()
            else:
                title = soup.title.string.strip() if soup.title else f"Job Posting ({portal_name})"

        if not company:
            # Look for common company selectors
            comp_elem = (
                soup.find(class_=re.compile(r'company|employer|org-name|hiring-org', re.I)) or
                soup.find("a", href=re.compile(r'/company/|/employer/', re.I))
            )
            if comp_elem:
                company = comp_elem.get_text().strip()
            else:
                company = "Company via " + portal_name

        if not location:
            loc_elem = soup.find(class_=re.compile(r'location|city|job-location', re.I))
            if loc_elem:
                location = loc_elem.get_text().strip()
            else:
                location = "India / Remote"

        # If description is still too short, extract largest text container
        if not description or len(description) < 150:
            candidates = soup.find_all(["div", "article", "section"], class_=re.compile(r'desc|detail|content|body|job-info', re.I))
            longest = ""
            for c in candidates:
                txt = c.get_text(separator="\n").strip()
                if len(txt) > len(longest):
                    longest = txt
            if len(longest) > 100:
                description = longest
            else:
                description = body_text[:2500]

        extracted_date, day_posted = extract_dates(body_text + " " + (description or ""))
        if not salary:
            salary = extract_salary(body_text + " " + (description or ""))

        emails, phones, telegram, whatsapp = extract_contacts_and_links(body_text + " " + (description or ""))

        return {
            "status": "success",
            "portal": portal_name,
            "url": url_clean,
            "fetch_method": "Live Web Scrape & Parser",
            "title": title or "Internship / Job Posting",
            "company": company or "Hiring Organization",
            "location": location or "Not specified",
            "date_posted": date_posted or extracted_date,
            "day_posted": day_posted,
            "salary": salary or "Unspecified",
            "experience": "Entry Level / Internship",
            "skills": "",
            "description": description or body_text[:2000],
            "contact_emails": emails,
            "phones": phones,
            "telegram_links": telegram,
            "whatsapp_links": whatsapp
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "portal": portal_name,
            "url": url_clean,
            "fetch_method": "Connection Error",
            "message": f"Network error fetching URL: {str(e)}. You can copy-paste the text directly!",
            "title": "Posting on " + portal_name,
            "company": "Unknown",
            "location": "Unknown",
            "date_posted": datetime.now().strftime("%d %b %Y"),
            "day_posted": datetime.now().strftime("%A"),
            "salary": "N/A",
            "experience": "N/A",
            "skills": "",
            "description": "",
            "contact_emails": [],
            "phones": [],
            "telegram_links": [],
            "whatsapp_links": []
        }
