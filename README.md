
# 🛠️ camzzz multi-tool — Termux Edition

A powerful OSINT / Network / Web / Hash toolkit running entirely on Android via Termux.  
Un outil OSINT / Réseau / Web / Hash qui tourne entièrement sur Android via Termux.

⚠️ Educational & authorized use only / Usage éducatif et autorisé uniquement

---

## 📌 About / À propos

This version is adapted from my **main camzzz multi-tool** and optimized to run on **Termux (Android)**.  
Certain features come directly from the main version and have been adapted to ensure compatibility, stability, and performance on mobile.

Cette version est **adaptée de mon multi-tool principal** et optimisée pour fonctionner sur **Termux (Android)**.  
Certaines fonctionnalités proviennent directement de la version principale et ont été adaptées pour garantir compatibilité et stabilité sur mobile.

---

## 🚀 Features / Fonctionnalités

### 🌐 Network (6 modules)

| # | Module | Description |
|--|--------|------------|
| 01 | IP Lookup & Tracker | Your IP or any IP, reputation links, Google Maps |
| 02 | DNS Lookup | A, AAAA, MX, NS, TXT, CNAME, SOA, CAA + reverse DNS |
| 03 | WHOIS Lookup | Full domain WHOIS data |
| 04 | Port Scanner | Multithreaded — common / top 1024 / custom range |
| 05 | Subdomain Finder | 80+ wordlist, multithreaded with progress bar |
| 06 | ASN / BGP Lookup | Prefix, ASN, country, peers via BGPView |

---

### 🌍 Web (5 modules)

| # | Module | Description |
|--|--------|------------|
| 07 | HTTP Header Inspector | Full headers + security audit (score A/B/C/D) |
| 08 | SSL Certificate Inspector | Subject, issuer, SANs, days until expiry |
| 09 | Tech Detector | 30+ CMS / frameworks / analytics detection |
| 10 | URL Redirect Tracer | Full redirect chain with status codes |
| 10b | WAF Detector | 12 WAF signatures + CDN detection |

---

### 🔎 OSINT (4 modules)

| # | Module | Description |
|--|--------|------------|
| 11 | Username Tracker | 50+ platforms, multithreaded, progress bar |
| 12 | Email OSINT | Disposable check, MX, format guesser, OSINT links |
| 13 | Phone Number Info | 70+ countries, FR line type, OSINT links |
| 14 | Metadata Extractor | EXIF + GPS coordinates + Google Maps link |

---

### 🔐 Hash / Password (3 modules)

| # | Module | Description |
|--|--------|------------|
| 15 | Hash Generator | MD5, SHA1, SHA256, SHA512, SHA3-256, Base64 |
| 16 | Hash Cracker | Wordlist attack, auto-detects hash type |
| 17 | Password Generator | Secure random + strength tester |

---

## 📱 Installation on Termux (Android)

### 1️⃣ Install Termux

Download Termux from F-Droid (recommended) or Play Store:

👉 https://f-droid.org/packages/com.termux/

---

### 2️⃣ Update system and install dependencies

```bash
pkg update && pkg upgrade -y
pkg install python git libjpeg-turbo libpng freetype clang openssl -y
````

---

### 3️⃣ Get the tool

**Option A — Clone from GitHub**

```bash
git clone https://github.com/cameleonnbss/Termux-tool-
cd Termux-tool-
```

**Option B — Copy from phone storage**

```bash
termux-setup-storage
cp /sdcard/Download/camzzz-tool.py ~/
cd ~
```

**Option C — Manual**

```bash
nano ~/camzzz-tool.py
```

---

### 4️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Fix common errors (Termux)

**Pillow issue**

```bash
pkg install libjpeg-turbo libpng freetype clang -y
pip install pillow
```

**python-whois issue**

```bash
pip install python-whois --break-system-packages
```

---

### 5️⃣ Run

```bash
python camzzz-tool.py
```

---

## 🖥️ Installation on Linux

### Debian / Ubuntu / Kali

```bash
sudo apt update && sudo apt install python3 python3-pip git -y
git clone https://github.com/cameleonnbss/Termux-tool-
cd Termux-tool-
pip3 install -r requirements.txt
python3 camzzz-tool.py
```

---

### Arch / Manjaro

```bash
sudo pacman -S python python-pip git
git clone https://github.com/cameleonnbss/Termux-tool-
cd Termux-tool-
pip install -r requirements.txt
python camzzz-tool.py
```

---

## 🪟 Installation on Windows

```bash
# Install Python 3.10+ from https://python.org (check "Add to PATH")
git clone https://github.com/cameleonnbss/Termux-tool-
cd Termux-tool-
pip install -r requirements.txt
python camzzz-tool.py
```

> If `python` is not recognized, try `py`

---

## 📦 Dependencies

| Package        | Usage            |
| -------------- | ---------------- |
| requests       | HTTP requests    |
| colorama       | Colored terminal |
| dnspython      | DNS queries      |
| python-whois   | WHOIS            |
| beautifulsoup4 | HTML parsing     |
| lxml           | Fast parser      |
| httpx          | Advanced HTTP    |
| rich           | CLI UI           |
| Pillow         | Image metadata   |
| exifread       | EXIF extraction  |

---

## ⚠️ Disclaimer / Avertissement

This project is for educational and authorized security research purposes only.
Do NOT use this tool on systems or people without explicit authorization.
The author is not responsible for any misuse.

Ce projet est uniquement destiné à l'apprentissage et à la recherche en sécurité autorisée.
N'utilise pas cet outil sans autorisation explicite.
L'auteur décline toute responsabilité en cas de mauvaise utilisation.

---

## 👨‍💻 Author / Auteur

camzzz

Discord : cameleonmortis
GitHub : [https://github.com/cameleonnbss](https://github.com/cameleonnbss)

---

 Status

Termux ✔
Linux ✔
Windows ✔

```
