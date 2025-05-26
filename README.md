# WebRecon – Smart Wordlist & Email Reconnaissance Tool

**WebRecon** is a Python tool for intelligent web reconnaissance. It crawls a target website, extracts a custom wordlist, scrapes real email addresses, and intelligently guesses potential emails using keywords and names from the website content—even on IP-based or local targets.

---

## 🔍 Features

- 🕷️ Crawl up to a specified number of pages using `--limit`
- 📚 Custom wordlist generation from content
- 📧 Email scraping from live pages
- 🤖 Smart email guessing using headings and inferred domains
- 🧠 Wordlist-based domain guessing even for IP-based/local targets
- 📁 Organized output in `output/<folder>/`

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### With a Domain URL:
```bash
python webrecon.py --domain https://example.com --limit 5 --depth 2
```

### With an IP-based URL:
```bash
python webrecon.py --ip http://192.168.0.10:8080 --limit 10
```

### Optional: Override Output Folder Name
```bash
python webrecon.py --domain https://example.com --limit 5 --output-name myrecon
```

---

## 📁 Output

Files are saved in `output/<folder>/`, where `<folder>` is:
- The registered domain (`example.com`)
- The host/IP (`192_168_0_10`)
- Or a custom name (if `--output-name` is used)

### Files:
```
webrecon.py
requirements.txt
README.md
output/
└── example.com/
    ├── wordlist.txt         # Extracted keywords
    ├── emails.txt           # Scraped live emails
    └── guessed_emails.txt   # Smart guessed emails
```

---

## 🧠 Email Guessing Logic

- Extracts names from headings, titles, and paragraphs
- Builds common username formats: `john.doe`, `jdoe`, etc.
- Guesses realistic domains using top 20 scraped words
- Combines them to form results like:
```
support@juiceshop.local
john@portal.shop.org
admin@juice.internal
```

---


## ⚠️ Legal Notice

**Use only on sites you own or have permission to test.** This tool is meant for **educational and authorized penetration testing** only.

---

## 👨‍💻 Author

Created by Lokesh Lankalapalli for project portfolio.
