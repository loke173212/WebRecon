
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import tldextract
import argparse
import os
from collections import Counter

def crawl(url, visited, to_visit, max_pages):
    if not to_visit or len(visited) >= max_pages:
        return

    next_url = to_visit.pop(0)
    if next_url in visited:
        return crawl(url, visited, to_visit, max_pages)

    try:
        response = requests.get(next_url, timeout=5)
        visited.add(next_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for a_tag in soup.find_all('a', href=True):
            link = urljoin(url, a_tag['href'])
            if urlparse(link).netloc == urlparse(url).netloc and link not in visited:
                to_visit.append(link)

        print(f"[+] Crawled: {next_url}")
        crawl(url, visited, to_visit, max_pages)

    except Exception as e:
        print(f"[-] Failed to crawl {next_url}: {e}")
        crawl(url, visited, to_visit, max_pages)

def extract_words_and_emails(html):
    words = set(re.findall(r'\b[a-zA-Z]{4,}\b', html))
    emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
    return words, emails

def guess_domains_from_wordlist(words):
    blacklist = {"this", "that", "with", "from", "home", "page", "your", "login", 
                 "signup", "about", "help", "click", "html", "submit", "read", "more", 
                 "back", "next", "here", "search", "true", "false"}

    clean_words = [w.lower() for w in words if w.isalpha() and len(w) > 3 and w.lower() not in blacklist]
    common = [word for word, _ in Counter(clean_words).most_common(20)]

    domains = set()
    for word in common:
        domains.update([
            word,
            f"{word}.com",
            f"{word}.org",
            f"{word}.net",
            f"{word}.co",
            f"{word}.local",
            f"secure.{word}",
            f"portal.{word}",
            f"admin.{word}",
            f"{word}.internal"
        ])
    return domains

def guess_emails_from_content(html, domain_guesses):
    soup = BeautifulSoup(html, 'html.parser')
    text_blocks = soup.get_text(separator=' ', strip=True)

    raw_words = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text_blocks))
    raw_words.update([tag.get_text().strip() for tag in soup.find_all(['h1', 'h2', 'h3', 'title']) if tag.get_text()])
    words = {w.lower() for w in raw_words if 3 < len(w) < 25 and not w.lower().startswith(('http', 'www'))}

    names = [w for w in words if ' ' in w or w.isalpha()]
    usernames = set()
    for name in names:
        parts = name.split()
        if len(parts) == 2:
            f, l = parts
            usernames.update([
                f"{f}.{l}", f"{f[0]}{l}", f"{l}.{f}", f"{f}", f"{l}", f"{f}{l}", f"{f}_{l}"
            ])
        else:
            usernames.add(name)

    usernames.update(['admin', 'info', 'support', 'hr', 'webmaster'])

    guessed_emails = set()
    for user in usernames:
        for domain in domain_guesses:
            guessed_emails.add(f"{user}@{domain}")
    return guessed_emails

def save_results(words, emails_found, guessed_emails, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "wordlist.txt"), "w") as f:
        for word in sorted(words):
            f.write(word + "\n")

    with open(os.path.join(output_dir, "emails.txt"), "w") as f:
        for email in sorted(emails_found):
            f.write(email + "\n")

    with open(os.path.join(output_dir, "guessed_emails.txt"), "w") as f:
        for email in sorted(guessed_emails):
            f.write(email + "\n")

def main():
    parser = argparse.ArgumentParser(description="Website Recon Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--domain", help="Target website URL with domain")
    group.add_argument("--ip", help="Target website URL with IP address")
    parser.add_argument("--depth", type=int, default=2, help="(Deprecated) Depth limit (use --limit instead)")
    parser.add_argument("--limit", type=int, default=10, help="Max number of pages to crawl")
    parser.add_argument("--output-name", help="Override output folder name")
    args = parser.parse_args()

    url = args.domain if args.domain else args.ip
    visited = set()
    all_words = set()
    all_emails = set()
    sample_html = ""

    crawl(url, visited, [url], args.limit)

    for link in visited:
        try:
            r = requests.get(link, timeout=5)
            words, emails = extract_words_and_emails(r.text)
            all_words.update(words)
            all_emails.update(emails)
            if not sample_html:
                sample_html = r.text
        except:
            continue

    domain_guesses = guess_domains_from_wordlist(all_words)
    guessed_emails = guess_emails_from_content(sample_html, domain_guesses)

    if args.output_name:
        domain_folder = args.output_name
    else:
        ext = tldextract.extract(url)
        domain_folder = ext.registered_domain or urlparse(url).hostname.replace('.', '_')

    output_dir = os.path.join("output", domain_folder)

    save_results(all_words, all_emails, guessed_emails, output_dir)

    print(f"\n✅ Scan complete.")
    print(f"  - Unique pages crawled: {len(visited)}")
    print(f"  - Words extracted: {len(all_words)}")
    print(f"  - Emails found: {len(all_emails)}")
    print(f"  - Guessed emails: {len(guessed_emails)}")
    print(f"  - Results saved in '{output_dir}' directory.")

if __name__ == "__main__":
    main()
