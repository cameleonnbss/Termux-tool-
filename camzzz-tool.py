#!/usr/bin/env python3
"""
camzzz multi-tool — Termux Edition
OSINT / Network / Web / Hash — By camzzz
Educational purposes only.
"""

import os, sys, ssl, json, socket, hashlib, secrets, string
import threading, platform, time, re, ipaddress
from datetime import datetime

# ── dependency check ──────────────────────────────────────
def require(pkg, import_as=None):
    try:
        return __import__(import_as or pkg)
    except ImportError:
        print(f"[!] Missing: {pkg}  →  pip install {pkg}")
        sys.exit(1)

requests  = require("requests")
colorama  = require("colorama")
from colorama import Fore, Style, init
init(autoreset=True)

try:
    import whois as _whois; WHOIS_OK = True
except ImportError:
    WHOIS_OK = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_OK = True
except ImportError:
    PIL_OK = False

system = platform.system().lower()
VERSION = "1.0 — Termux Edition"

# ══════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════

def clear():
    os.system("cls" if system == "windows" else "clear")

def pause():
    input(Fore.WHITE + "\n  [ Press ENTER to return to menu ] ")

def banner_line(char="═", width=58):
    return Fore.CYAN + char * width

def section(title, color=Fore.CYAN):
    print()
    print(color + "╔" + "═"*56 + "╗")
    print(color + "║" + f"  {title}".ljust(56) + "║")
    print(color + "╚" + "═"*56 + "╝")
    print()

def info(label, value, lw=26):
    print(Fore.GREEN + f"  {label:<{lw}}" + Fore.WHITE + f": {value}")

def ok(msg):    print(Fore.GREEN  + f"  [✔] {msg}")
def warn(msg):  print(Fore.YELLOW + f"  [!] {msg}")
def err(msg):   print(Fore.RED    + f"  [✘] {msg}")
def link(url):  print(Fore.CYAN   + f"  → {url}")

def spinner(msg, seconds=1.5):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        print(Fore.YELLOW + f"\r  {frames[i % len(frames)]}  {msg}", end="", flush=True)
        time.sleep(0.1); i += 1
    print("\r" + " "*60 + "\r", end="")

def progress_bar(current, total, width=40, label=""):
    pct = current / total
    filled = int(width * pct)
    bar = Fore.GREEN + "█"*filled + Fore.WHITE + "░"*(width-filled)
    print(f"\r  [{bar}{Fore.WHITE}] {int(pct*100):3d}%  {label}", end="", flush=True)

def tag(text, color=Fore.GREEN):
    return color + f"[{text}]" + Fore.WHITE

REQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    )
}

def get(url, timeout=8, **kw):
    return requests.get(url, headers=REQ_HEADERS, timeout=timeout, **kw)

# ══════════════════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════════════════

def banner():
    print(Fore.GREEN + r"""
  ██████╗ █████╗ ███╗   ███╗███████╗███████╗███████╗
 ██╔════╝██╔══██╗████╗ ████║╚══███╔╝╚══███╔╝╚══███╔╝
 ██║     ███████║██╔████╔██║  ███╔╝   ███╔╝   ███╔╝
 ██║     ██╔══██║██║╚██╔╝██║ ███╔╝   ███╔╝   ███╔╝
 ╚██████╗██║  ██║██║ ╚═╝ ██║███████╗███████╗███████╗
  ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝""")
    print(Fore.YELLOW + f"\n  multi-tool {VERSION} — By camzzz")
    print(Fore.WHITE  +  "  Discord: cameleonmortis  |  github.com/cameleonnbss")
    print(Fore.RED    +  "  [!] Educational & authorized use only\n")

# ══════════════════════════════════════════════════════════════════
#  01 — IP LOOKUP & TRACKER
# ══════════════════════════════════════════════════════════════════

def ip_lookup():
    clear(); banner(); section("🌐  IP LOOKUP & TRACKER")
    print(Fore.CYAN + "  (1) My public IP    (2) Lookup any IP\n")
    c = input(Fore.WHITE + "  > ").strip()
    if c == "1":
        spinner("Fetching your public IP...")
        try:
            r = get("https://ipapi.co/json/")
            d = r.json()
            ip = d.get("ip","?")
        except Exception as e:
            err(f"Failed: {e}"); pause(); return
    else:
        ip = input(Fore.WHITE + "  IP > ").strip()
        if not ip: pause(); return
        spinner(f"Looking up {ip}...")
        try:
            d = get(f"https://ipapi.co/{ip}/json/").json()
        except Exception as e:
            err(f"Failed: {e}"); pause(); return

    print()
    fields = [
        ("IP",              d.get("ip")),
        ("City",            d.get("city")),
        ("Region",          d.get("region")),
        ("Country",         d.get("country_name")),
        ("Postal",          d.get("postal")),
        ("Latitude",        d.get("latitude")),
        ("Longitude",       d.get("longitude")),
        ("Timezone",        d.get("timezone")),
        ("ISP / Org",       d.get("org")),
        ("ASN",             d.get("asn")),
        ("Currency",        d.get("currency_name")),
        ("Languages",       d.get("languages")),
    ]
    for label, val in fields:
        if val: info(label, val)

    lat, lon = d.get("latitude",""), d.get("longitude","")
    if lat and lon:
        print()
        link(f"https://www.google.com/maps?q={lat},{lon}")

    # reputation check
    print()
    warn("Reputation check links:")
    link(f"https://www.abuseipdb.com/check/{ip}")
    link(f"https://otx.alienvault.com/indicator/ip/{ip}")
    link(f"https://shodan.io/host/{ip}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  02 — DNS LOOKUP
# ══════════════════════════════════════════════════════════════════

DNS_RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "CAA"]

def dns_lookup():
    clear(); banner(); section("🌐  DNS LOOKUP")
    domain = input(Fore.WHITE + "  Domain > ").strip()
    if not domain: pause(); return

    spinner(f"Querying DNS for {domain}...")

    # use Google DoH (works on Termux without dnspython)
    results = {}
    for rtype in DNS_RECORD_TYPES:
        try:
            r = get(
                f"https://dns.google/resolve?name={domain}&type={rtype}",
                timeout=6
            ).json()
            answers = r.get("Answer", [])
            if answers:
                results[rtype] = [a.get("data","") for a in answers]
        except Exception:
            pass

    print()
    if not results:
        err("No DNS records found.")
    else:
        for rtype, values in results.items():
            for v in values:
                info(rtype, v)

    # also do a reverse lookup on the A record
    a_records = results.get("A", [])
    if a_records:
        print()
        try:
            rev = socket.gethostbyaddr(a_records[0])
            info("Reverse (PTR)", rev[0])
        except Exception:
            pass
    pause()

# ══════════════════════════════════════════════════════════════════
#  03 — WHOIS LOOKUP
# ══════════════════════════════════════════════════════════════════

def whois_lookup():
    clear(); banner(); section("🌐  WHOIS LOOKUP")
    if not WHOIS_OK:
        err("python-whois not installed.")
        warn("Run: pip install python-whois"); pause(); return

    domain = input(Fore.WHITE + "  Domain > ").strip()
    if not domain: pause(); return
    spinner(f"Querying WHOIS for {domain}...")

    try:
        w = _whois.whois(domain)
        print()
        fields = [
            ("Domain",          w.domain_name),
            ("Registrar",       w.registrar),
            ("Created",         w.creation_date),
            ("Expires",         w.expiration_date),
            ("Updated",         w.updated_date),
            ("Status",          w.status),
            ("Name Servers",    w.name_servers),
            ("Emails",          w.emails),
            ("Country",         w.country),
            ("Org",             w.org),
            ("DNSSEC",          w.dnssec),
        ]
        for label, val in fields:
            if val:
                if isinstance(val, list): val = ", ".join(str(v) for v in val[:4])
                info(label, str(val)[:80])
    except Exception as e:
        err(f"WHOIS failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  04 — PORT SCANNER
# ══════════════════════════════════════════════════════════════════

TOP_PORTS = {
    21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 53:"DNS",
    80:"HTTP", 110:"POP3", 143:"IMAP", 443:"HTTPS", 445:"SMB",
    993:"IMAPS", 995:"POP3S", 1433:"MSSQL", 1521:"Oracle",
    3306:"MySQL", 3389:"RDP", 5432:"PostgreSQL", 5900:"VNC",
    6379:"Redis", 8080:"HTTP-Alt", 8443:"HTTPS-Alt",
    8888:"Jupyter", 9200:"Elasticsearch", 27017:"MongoDB",
}

_open_ports = []
_port_lock  = threading.Lock()

def _scan_port(host, port, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        if s.connect_ex((host, port)) == 0:
            svc = TOP_PORTS.get(port, "?")
            with _port_lock:
                _open_ports.append((port, svc))
        s.close()
    except Exception:
        pass

def port_scanner():
    clear(); banner(); section("🌐  PORT SCANNER")
    target = input(Fore.WHITE + "  Target host/IP > ").strip()
    if not target: pause(); return

    print(Fore.CYAN + "\n  Scan mode:")
    print("  (1) Common ports (24)   (2) Top 1024   (3) Custom range\n")
    mode = input(Fore.WHITE + "  > ").strip()

    try:
        host_ip = socket.gethostbyname(target)
    except socket.gaierror as e:
        err(f"Cannot resolve: {e}"); pause(); return

    global _open_ports
    _open_ports = []

    if mode == "2":
        ports = list(range(1, 1025))
        timeout = 0.4
    elif mode == "3":
        try:
            s = int(input("  Start port > "))
            e2 = int(input("  End port   > "))
            ports = list(range(s, e2+1))
            timeout = 0.4
        except ValueError:
            err("Invalid range."); pause(); return
    else:
        ports = list(TOP_PORTS.keys())
        timeout = 0.5

    print(Fore.YELLOW + f"\n  Scanning {len(ports)} ports on {target} ({host_ip})...\n")
    threads = [threading.Thread(target=_scan_port, args=(host_ip, p, timeout)) for p in ports]
    total = len(threads)
    for i, t in enumerate(threads):
        t.start()
        if i % 10 == 0:
            progress_bar(i, total)
    for t in threads: t.join()
    progress_bar(total, total); print()

    print()
    if _open_ports:
        for port, svc in sorted(_open_ports):
            ok(f"Port {port:<6}  {svc}")
    else:
        warn("No open ports found.")
    pause()

# ══════════════════════════════════════════════════════════════════
#  05 — SUBDOMAIN FINDER
# ══════════════════════════════════════════════════════════════════

SUBDOMAIN_WORDLIST = [
    "www","mail","ftp","remote","blog","webmail","server","ns1","ns2",
    "smtp","secure","vpn","m","shop","api","dev","staging","test",
    "portal","admin","dashboard","support","forum","cdn","static",
    "img","images","media","git","gitlab","jenkins","ci","beta","demo",
    "app","apps","mobile","web","help","docs","old","new","backup",
    "mx","pop","imap","smtp2","mail2","ns3","ns4","cpanel","whm",
    "autodiscover","autoconfig","office","login","sso","auth","oauth",
    "payment","pay","store","billing","account","accounts","my",
    "cdn2","assets","upload","uploads","download","downloads","s3",
    "aws","azure","cloud","proxy","gateway","waf","firewall","vpn2",
    "monitor","status","health","api2","v1","v2","beta2","sandbox",
    "uat","qa","prod","preview","internal","intranet","extranet",
]

_found_subs = []
_sub_lock   = threading.Lock()

def _check_sub(sub, domain):
    full = f"{sub}.{domain}"
    try:
        ip = socket.gethostbyname(full)
        with _sub_lock:
            _found_subs.append((full, ip))
    except socket.gaierror:
        pass

def subdomain_finder():
    clear(); banner(); section("🌐  SUBDOMAIN FINDER")
    domain = input(Fore.WHITE + "  Domain (example.com) > ").strip()
    if not domain: pause(); return

    global _found_subs
    _found_subs = []
    total = len(SUBDOMAIN_WORDLIST)
    print(Fore.YELLOW + f"\n  Scanning {total} subdomains...\n")

    threads = [threading.Thread(target=_check_sub, args=(s, domain)) for s in SUBDOMAIN_WORDLIST]
    for i, t in enumerate(threads):
        t.start()
        if i % 8 == 0: progress_bar(i, total)
    for t in threads: t.join()
    progress_bar(total, total); print("\n")

    if _found_subs:
        for full, ip in sorted(_found_subs):
            ok(f"{full:<45} {ip}")
        print(Fore.YELLOW + f"\n  {len(_found_subs)} subdomains found.")
    else:
        warn("No subdomains found.")
    pause()

# ══════════════════════════════════════════════════════════════════
#  06 — ASN / BGP LOOKUP
# ══════════════════════════════════════════════════════════════════

def asn_lookup():
    clear(); banner(); section("🌐  ASN / BGP LOOKUP")
    target = input(Fore.WHITE + "  IP or ASN (e.g. AS15169) > ").strip()
    if not target: pause(); return
    spinner("Querying BGPView...")
    try:
        if target.upper().startswith("AS"):
            asn = target.upper().replace("AS","")
            r = get(f"https://api.bgpview.io/asn/{asn}").json()
            d = r.get("data", {})
            print()
            info("ASN",           f"AS{d.get('asn','?')}")
            info("Name",          d.get("name","?"))
            info("Description",   d.get("description_short","?"))
            info("Country",       d.get("country_code","?"))
            info("RIR",           d.get("rir_allocation",{}).get("rir_name","?"))
            info("Prefixes IPv4", str(d.get("prefixes_count_ipv4","?")))
            info("Prefixes IPv6", str(d.get("prefixes_count_ipv6","?")))
            info("Peers IPv4",    str(d.get("peers_count_ipv4","?")))
        else:
            r = get(f"https://api.bgpview.io/ip/{target}").json()
            prefixes = r.get("data",{}).get("prefixes",[])
            print()
            for p in prefixes[:5]:
                info("Prefix",   p.get("prefix","?"))
                info("ASN",      f"AS{p.get('asn',{}).get('asn','?')}")
                info("Name",     p.get("asn",{}).get("name","?"))
                info("Country",  p.get("country_code","?"))
                print()
    except Exception as e:
        err(f"Failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  07 — HTTP HEADER INSPECTOR
# ══════════════════════════════════════════════════════════════════

SECURITY_HEADERS = {
    "Strict-Transport-Security": "HSTS",
    "Content-Security-Policy":   "CSP",
    "X-Frame-Options":           "Clickjacking protection",
    "X-Content-Type-Options":    "MIME sniffing protection",
    "Referrer-Policy":           "Referrer policy",
    "Permissions-Policy":        "Permissions policy",
    "X-XSS-Protection":          "XSS protection",
    "Cross-Origin-Opener-Policy":"COOP",
}

def http_headers():
    clear(); banner(); section("🌍  HTTP HEADER INSPECTOR")
    site = input(Fore.WHITE + "  URL (example.com) > ").strip()
    if not site: pause(); return
    if not site.startswith("http"): site = "https://" + site
    spinner(f"Inspecting {site}...")
    try:
        r = get(site, timeout=10, allow_redirects=True)
        h = r.headers
        print()
        info("URL",          r.url)
        info("Status",       str(r.status_code))
        info("Server",       h.get("Server","N/A"))
        info("Powered-By",   h.get("X-Powered-By","N/A"))
        info("Content-Type", h.get("Content-Type","N/A"))
        info("Cache-Control",h.get("Cache-Control","N/A"))
        info("Cookies",      str(len(r.cookies)) + " cookie(s)")

        print(Fore.CYAN + "\n  ── Security Headers Audit ──\n")
        score = 0
        for header, desc in SECURITY_HEADERS.items():
            if header in h:
                ok(f"{desc:<35} {header}")
                score += 1
            else:
                err(f"{desc:<35} MISSING")

        grade = "A" if score>=7 else "B" if score>=5 else "C" if score>=3 else "D"
        color = Fore.GREEN if grade=="A" else Fore.YELLOW if grade in ("B","C") else Fore.RED
        print(color + f"\n  Security Score: {score}/{len(SECURITY_HEADERS)}  Grade: {grade}\n")

    except Exception as e:
        err(f"Failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  08 — SSL CERTIFICATE INSPECTOR
# ══════════════════════════════════════════════════════════════════

def ssl_inspector():
    clear(); banner(); section("🌍  SSL CERTIFICATE INSPECTOR")
    host = input(Fore.WHITE + "  Host (example.com) > ").strip()
    if not host: pause(); return
    spinner(f"Inspecting SSL for {host}...")
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(8)
            s.connect((host, 443))
            cert = s.getpeercert()

        print()
        subject = dict(x[0] for x in cert.get("subject",[]))
        issuer  = dict(x[0] for x in cert.get("issuer", []))

        info("Common Name",   subject.get("commonName","?"))
        info("Organization",  subject.get("organizationName","?"))
        info("Issued By",     issuer.get("organizationName","?"))
        info("Valid From",    cert.get("notBefore","?"))
        info("Expires",       cert.get("notAfter","?"))
        info("Version",       str(cert.get("version","?")))
        info("Serial",        str(cert.get("serialNumber","?")))

        # expiry check
        exp_str = cert.get("notAfter","")
        if exp_str:
            exp = datetime.strptime(exp_str, "%b %d %H:%M:%S %Y %Z")
            days_left = (exp - datetime.utcnow()).days
            color = Fore.GREEN if days_left > 30 else Fore.YELLOW if days_left > 7 else Fore.RED
            print(color + f"\n  ⏳ Expires in {days_left} days")

        sans = cert.get("subjectAltName",[])
        if sans:
            print(Fore.CYAN + "\n  Subject Alternative Names (SANs):")
            for _, san in sans[:10]:
                print(Fore.WHITE + f"    • {san}")

    except ssl.SSLCertVerificationError as e:
        err(f"SSL verification error: {e}")
    except Exception as e:
        err(f"Failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  09 — TECH DETECTOR
# ══════════════════════════════════════════════════════════════════

TECH_SIGNATURES = {
    # CMS
    "WordPress":       [r"wp-content", r"wp-includes", r"WordPress"],
    "Joomla":          [r"Joomla!", r"/components/com_"],
    "Drupal":          [r"Drupal", r"/sites/default/files"],
    "Magento":         [r"Magento", r"Mage.Cookies"],
    "Shopify":         [r"cdn.shopify.com", r"Shopify.theme"],
    "Wix":             [r"wix.com", r"X-Wix-Published-Version"],
    "Ghost":           [r"ghost.io", r"/ghost/api/"],
    # Frameworks
    "React":           [r"react", r"__REACT_DEVTOOLS"],
    "Vue.js":          [r"vue\.js", r"__vue__"],
    "Angular":         [r"ng-version", r"angular.min.js"],
    "Next.js":         [r"__NEXT_DATA__", r"_next/static"],
    "Nuxt.js":         [r"__NUXT__", r"_nuxt/"],
    "Laravel":         [r"laravel_session", r"Laravel"],
    "Django":          [r"csrfmiddlewaretoken", r"Django"],
    "Ruby on Rails":   [r"X-Runtime.*Ruby", r"rails"],
    # Servers
    "Nginx":           [r"nginx"],
    "Apache":          [r"Apache"],
    "Cloudflare":      [r"cf-ray", r"cloudflare"],
    "Varnish":         [r"X-Varnish"],
    "IIS":             [r"X-Powered-By.*ASP.NET", r"Microsoft-IIS"],
    # Analytics
    "Google Analytics":[r"google-analytics.com", r"gtag\("],
    "Google Tag Mgr":  [r"googletagmanager.com"],
    # Other
    "Bootstrap":       [r"bootstrap.min.css", r"bootstrap.min.js"],
    "jQuery":          [r"jquery"],
    "Font Awesome":    [r"font-awesome", r"fontawesome"],
    "reCAPTCHA":       [r"recaptcha"],
}

def tech_detector():
    clear(); banner(); section("🌍  TECH DETECTOR")
    site = input(Fore.WHITE + "  URL (example.com) > ").strip()
    if not site: pause(); return
    if not site.startswith("http"): site = "https://" + site
    spinner(f"Detecting technologies on {site}...")
    try:
        r = get(site, timeout=10, allow_redirects=True)
        body = r.text.lower()
        raw_headers = str(r.headers).lower()
        combined = body + raw_headers

        detected = []
        for tech, patterns in TECH_SIGNATURES.items():
            for pat in patterns:
                if re.search(pat.lower(), combined):
                    detected.append(tech)
                    break

        print()
        if detected:
            for tech in detected:
                ok(tech)
            print(Fore.YELLOW + f"\n  {len(detected)} technologies detected.")
        else:
            warn("No known technologies detected.")

    except Exception as e:
        err(f"Failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  10 — URL REDIRECT TRACER
# ══════════════════════════════════════════════════════════════════

def redirect_tracer():
    clear(); banner(); section("🌍  URL REDIRECT TRACER")
    url = input(Fore.WHITE + "  URL > ").strip()
    if not url: pause(); return
    if not url.startswith("http"): url = "https://" + url

    print(Fore.YELLOW + "\n  Tracing redirect chain...\n")
    try:
        r = get(url, allow_redirects=False, timeout=8)
        hops = 0
        current = url
        print(Fore.CYAN + f"  [0] {current}")
        while r.is_redirect or r.status_code in (301,302,303,307,308):
            hops += 1
            loc = r.headers.get("Location","")
            if not loc: break
            if loc.startswith("/"): loc = "/".join(current.split("/")[:3]) + loc
            color = Fore.YELLOW if r.status_code in (301,308) else Fore.GREEN
            print(color + f"  [{hops}] {r.status_code} → {loc}")
            current = loc
            try:
                r = get(current, allow_redirects=False, timeout=8)
            except Exception:
                break
            if hops > 15:
                warn("Too many redirects (>15), stopping."); break

        print(Fore.GREEN + f"\n  Final URL: {current}")
        print(Fore.WHITE + f"  Total hops: {hops}")
    except Exception as e:
        err(f"Failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  10b — WAF DETECTOR
# ══════════════════════════════════════════════════════════════════

WAF_SIGNATURES = {
    "Cloudflare":      ["cf-ray","cloudflare","__cfduid"],
    "AWS WAF":         ["awswaf","x-amzn-requestid","x-amz"],
    "Akamai":          ["akamai","akamaierror","akamai-grn"],
    "Sucuri":          ["sucuri","x-sucuri-id","x-sucuri-cache"],
    "Incapsula":       ["incap_ses","visid_incap","x-iinfo"],
    "F5 BIG-IP":       ["bigipserver","x-cnection","f5-"],
    "ModSecurity":     ["mod_security","modsecurity","nss-agent"],
    "Barracuda":       ["barra_counter_session","barracuda_"],
    "Wordfence":       ["wordfence"],
    "Imperva":         ["imperva","x-iinfo","incapsula"],
    "Fastly":          ["fastly","x-fastly"],
    "Varnish":         ["x-varnish","via.*varnish"],
}

def waf_detector():
    clear(); banner(); section("🌍  WAF DETECTOR")
    site = input(Fore.WHITE + "  URL (example.com) > ").strip()
    if not site: pause(); return
    if not site.startswith("http"): site = "https://" + site
    spinner(f"Detecting WAF on {site}...")
    try:
        r = get(site, timeout=10)
        combined = (str(r.headers) + r.text).lower()
        cookies  = str(r.cookies).lower()
        all_data = combined + cookies

        found = []
        for waf, sigs in WAF_SIGNATURES.items():
            for sig in sigs:
                if sig.lower() in all_data:
                    found.append(waf)
                    break

        print()
        if found:
            for waf in found:
                ok(f"WAF detected: {waf}")
        else:
            warn("No known WAF detected (may be hidden or absent).")

        # CDN check
        server = r.headers.get("Server","").lower()
        via    = r.headers.get("Via","").lower()
        if "cloudfront" in server+via: info("CDN","Amazon CloudFront")
        if "fastly"     in server+via: info("CDN","Fastly")
        if "varnish"    in server+via: info("CDN","Varnish Cache")

    except Exception as e:
        err(f"Failed: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  11 — USERNAME TRACKER
# ══════════════════════════════════════════════════════════════════

USERNAME_SITES = {
    "GitHub":       ("https://github.com/{u}",          ["Not Found"]),
    "GitLab":       ("https://gitlab.com/{u}",          ["404"]),
    "Instagram":    ("https://www.instagram.com/{u}/",  ["Sorry, this page"]),
    "Twitter/X":    ("https://twitter.com/{u}",         ["This account doesn"]),
    "TikTok":       ("https://www.tiktok.com/@{u}",     ["Couldn't find"]),
    "Reddit":       ("https://www.reddit.com/user/{u}", ["Sorry, nobody"]),
    "Pinterest":    ("https://www.pinterest.com/{u}/",  ["404"]),
    "Twitch":       ("https://www.twitch.tv/{u}",       ["404"]),
    "Snapchat":     ("https://www.snapchat.com/add/{u}",["404"]),
    "YouTube":      ("https://www.youtube.com/@{u}",    ["404"]),
    "DeviantArt":   ("https://www.deviantart.com/{u}",  ["404"]),
    "Patreon":      ("https://www.patreon.com/{u}",     ["404"]),
    "Cashapp":      ("https://cash.app/${u}",           ["404"]),
    "Linktree":     ("https://linktr.ee/{u}",           ["404"]),
    "Keybase":      ("https://keybase.io/{u}",          ["404"]),
    "Steam":        ("https://steamcommunity.com/id/{u}",["The specified profile"]),
    "Spotify":      ("https://open.spotify.com/user/{u}",["404"]),
    "SoundCloud":   ("https://soundcloud.com/{u}",      ["404"]),
    "Replit":       ("https://replit.com/@{u}",         ["404"]),
    "HackerNews":   ("https://news.ycombinator.com/user?id={u}",["No such user"]),
    "ProductHunt":  ("https://www.producthunt.com/@{u}",["404"]),
    "Medium":       ("https://medium.com/@{u}",         ["404"]),
    "Tumblr":       ("https://{u}.tumblr.com",          ["There's nothing here"]),
    "Behance":      ("https://www.behance.net/{u}",     ["404"]),
    "Dribbble":     ("https://dribbble.com/{u}",        ["Whoops"]),
    "Vimeo":        ("https://vimeo.com/{u}",           ["404"]),
    "Flickr":       ("https://www.flickr.com/people/{u}",["404"]),
    "AboutMe":      ("https://about.me/{u}",            ["404"]),
    "Gravatar":     ("https://en.gravatar.com/{u}",     ["404"]),
    "Codecademy":   ("https://www.codecademy.com/profiles/{u}",["404"]),
    "Hackerearth":  ("https://www.hackerearth.com/@{u}",["404"]),
    "LeetCode":     ("https://leetcode.com/{u}",        ["404"]),
    "Codeforces":   ("https://codeforces.com/profile/{u}",["404"]),
    "NPM":          ("https://www.npmjs.com/~{u}",      ["404"]),
    "PyPI":         ("https://pypi.org/user/{u}/",      ["404"]),
    "DockerHub":    ("https://hub.docker.com/u/{u}",    ["404"]),
    "Mastodon":     ("https://mastodon.social/@{u}",    ["404"]),
    "Telegram":     ("https://t.me/{u}",                ["If you have Telegram"]),
    "VK":           ("https://vk.com/{u}",              ["404"]),
    "Weibo":        ("https://weibo.com/{u}",           ["404"]),
    "OK.ru":        ("https://ok.ru/{u}",               ["404"]),
    "Roblox":       ("https://www.roblox.com/user.aspx?username={u}",["404"]),
    "Minecraft":    ("https://namemc.com/profile/{u}",  ["404"]),
    "Kongregate":   ("https://www.kongregate.com/accounts/{u}",["404"]),
    "Newgrounds":   ("https://{u}.newgrounds.com",      ["404"]),
    "Fiverr":       ("https://www.fiverr.com/{u}",      ["404"]),
    "Freelancer":   ("https://www.freelancer.com/u/{u}",["404"]),
    "Upwork":       ("https://www.upwork.com/freelancers/~{u}",["404"]),
    "AngelList":    ("https://angel.co/{u}",            ["404"]),
    "Crunchbase":   ("https://www.crunchbase.com/person/{u}",["404"]),
}

_user_results = {}
_user_lock    = threading.Lock()

def _check_username(name, url, not_found_patterns, results):
    try:
        r = requests.get(url, headers=REQ_HEADERS, timeout=8, allow_redirects=True)
        if r.status_code == 404:
            results[name] = ("NOT FOUND", url)
        elif r.status_code == 200:
            body = r.text.lower()
            for pat in not_found_patterns:
                if pat.lower() in body:
                    results[name] = ("NOT FOUND", url)
                    return
            results[name] = ("FOUND", url)
        else:
            results[name] = (f"HTTP {r.status_code}", url)
    except Exception:
        results[name] = ("ERROR", url)

def username_tracker():
    clear(); banner(); section("🔎  USERNAME TRACKER")
    username = input(Fore.WHITE + "  Username > ").strip()
    if not username: pause(); return

    results = {}
    total = len(USERNAME_SITES)
    print(Fore.YELLOW + f"\n  Scanning {total} platforms...\n")

    threads = []
    for name, (tmpl, nfp) in USERNAME_SITES.items():
        url = tmpl.replace("{u}", username)
        t = threading.Thread(target=_check_username, args=(name, url, nfp, results))
        t.start()
        threads.append(t)

    for i, t in enumerate(threads):
        t.join()
        progress_bar(i+1, total, label=f"{i+1}/{total}")
    print("\n")

    found_count = 0
    for name in USERNAME_SITES:
        status, url = results.get(name, ("ERROR",""))
        if status == "FOUND":
            ok(f"{name:<18} {url}")
            found_count += 1
        elif status == "NOT FOUND":
            print(Fore.RED + f"  [✘] {name:<18} Not found")
        else:
            print(Fore.YELLOW + f"  [?] {name:<18} {status}")

    print(Fore.YELLOW + f"\n  {found_count}/{total} platforms: account found.")
    pause()

# ══════════════════════════════════════════════════════════════════
#  12 — EMAIL OSINT
# ══════════════════════════════════════════════════════════════════

DISPOSABLE_DOMAINS = {
    "mailinator.com","guerrillamail.com","tempmail.com","10minutemail.com",
    "throwam.com","sharklasers.com","trashmail.com","yopmail.com",
    "maildrop.cc","dispostable.com","fakeinbox.com","tempinbox.com",
}

def email_osint():
    clear(); banner(); section("🔎  EMAIL OSINT")
    email = input(Fore.WHITE + "  Email > ").strip()
    if "@" not in email:
        err("Invalid email."); pause(); return

    user, domain = email.split("@",1)
    print()
    info("Email",    email)
    info("Username", user)
    info("Domain",   domain)

    # disposable check
    if domain.lower() in DISPOSABLE_DOMAINS:
        warn("Disposable/temporary email service detected!")
    else:
        ok("Not a known disposable email service.")

    # format guesses
    fn = user.split(".")[0] if "." in user else user
    ln = user.split(".")[-1] if "." in user else ""
    if ln and fn != ln:
        print(Fore.CYAN + "\n  Possible name formats:")
        print(f"    First: {fn.capitalize()}  Last: {ln.capitalize()}")

    # DNS
    spinner(f"Querying DNS for {domain}...")
    try:
        ip = socket.gethostbyname(domain)
        print()
        info("Domain IP",  ip)
        try:
            rev = socket.gethostbyaddr(ip)
            info("Reverse",   rev[0])
        except Exception: pass
    except Exception:
        err("Could not resolve domain.")

    # MX check via Google DoH
    try:
        r = get(f"https://dns.google/resolve?name={domain}&type=MX").json()
        mx = [a.get("data","") for a in r.get("Answer",[])]
        if mx:
            print()
            for m in mx[:3]: info("MX Record", m)
    except Exception: pass

    # OSINT links
    print(Fore.CYAN + "\n  OSINT Links:")
    link(f"https://haveibeenpwned.com/account/{email}")
    link(f"https://hunter.io/email-verifier/{email}")
    link(f"https://www.google.com/search?q=%22{email}%22")
    link(f"https://www.linkedin.com/search/results/people/?keywords={email}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  13 — PHONE NUMBER INFO
# ══════════════════════════════════════════════════════════════════

PHONE_PREFIXES = {
    "+1":   ("USA / Canada", "NANP",  "en"),
    "+7":   ("Russia / Kazakhstan", "RU/KZ", "ru"),
    "+20":  ("Egypt", "EG", "ar"),
    "+27":  ("South Africa", "ZA", "en"),
    "+30":  ("Greece", "GR", "el"),
    "+31":  ("Netherlands", "NL", "nl"),
    "+32":  ("Belgium", "BE", "fr"),
    "+33":  ("France", "FR", "fr"),
    "+34":  ("Spain", "ES", "es"),
    "+36":  ("Hungary", "HU", "hu"),
    "+39":  ("Italy", "IT", "it"),
    "+40":  ("Romania", "RO", "ro"),
    "+41":  ("Switzerland", "CH", "de"),
    "+43":  ("Austria", "AT", "de"),
    "+44":  ("United Kingdom", "GB", "en"),
    "+45":  ("Denmark", "DK", "da"),
    "+46":  ("Sweden", "SE", "sv"),
    "+47":  ("Norway", "NO", "no"),
    "+48":  ("Poland", "PL", "pl"),
    "+49":  ("Germany", "DE", "de"),
    "+51":  ("Peru", "PE", "es"),
    "+52":  ("Mexico", "MX", "es"),
    "+54":  ("Argentina", "AR", "es"),
    "+55":  ("Brazil", "BR", "pt"),
    "+56":  ("Chile", "CL", "es"),
    "+57":  ("Colombia", "CO", "es"),
    "+58":  ("Venezuela", "VE", "es"),
    "+60":  ("Malaysia", "MY", "ms"),
    "+61":  ("Australia", "AU", "en"),
    "+62":  ("Indonesia", "ID", "id"),
    "+63":  ("Philippines", "PH", "en"),
    "+64":  ("New Zealand", "NZ", "en"),
    "+65":  ("Singapore", "SG", "en"),
    "+66":  ("Thailand", "TH", "th"),
    "+81":  ("Japan", "JP", "ja"),
    "+82":  ("South Korea", "KR", "ko"),
    "+84":  ("Vietnam", "VN", "vi"),
    "+86":  ("China", "CN", "zh"),
    "+90":  ("Turkey", "TR", "tr"),
    "+91":  ("India", "IN", "hi"),
    "+92":  ("Pakistan", "PK", "ur"),
    "+93":  ("Afghanistan", "AF", "ps"),
    "+94":  ("Sri Lanka", "LK", "si"),
    "+98":  ("Iran", "IR", "fa"),
    "+212": ("Morocco", "MA", "ar"),
    "+213": ("Algeria", "DZ", "ar"),
    "+216": ("Tunisia", "TN", "ar"),
    "+218": ("Libya", "LY", "ar"),
    "+221": ("Senegal", "SN", "fr"),
    "+234": ("Nigeria", "NG", "en"),
    "+254": ("Kenya", "KE", "sw"),
    "+351": ("Portugal", "PT", "pt"),
    "+352": ("Luxembourg", "LU", "fr"),
    "+353": ("Ireland", "IE", "en"),
    "+358": ("Finland", "FI", "fi"),
    "+380": ("Ukraine", "UA", "uk"),
    "+420": ("Czech Republic", "CZ", "cs"),
    "+421": ("Slovakia", "SK", "sk"),
    "+966": ("Saudi Arabia", "SA", "ar"),
    "+971": ("UAE", "AE", "ar"),
    "+972": ("Israel", "IL", "he"),
}

def phone_info():
    clear(); banner(); section("🔎  PHONE NUMBER INFO")
    number = input(Fore.WHITE + "  Phone number (e.g. +33612345678) > ").strip()
    if not number.startswith("+"):
        err("Include country code (e.g. +33...)"); pause(); return

    matched_prefix = matched_info = None
    for length in (4, 3, 2):
        prefix = number[:length]
        if prefix in PHONE_PREFIXES:
            matched_prefix = prefix
            matched_info   = PHONE_PREFIXES[prefix]
            break

    print()
    if matched_info:
        country, iso, lang = matched_info
        local  = number[len(matched_prefix):]
        digits = "".join(c for c in local if c.isdigit())
        info("Full number",   number)
        info("Country code",  matched_prefix)
        info("Country",       country)
        info("ISO code",      iso)
        info("Language",      lang)
        info("Local number",  local)
        info("Digit count",   str(len(digits)))

        # FR line type detection
        if matched_prefix == "+33" and digits:
            first = digits[0]
            types = {
                "6":"Mobile (SFR/Orange/Free/Bouygues)",
                "7":"Mobile (low-cost/MVNO)",
                "1":"Paris region landline",
                "2":"Northwest France landline",
                "3":"Northeast France landline",
                "4":"Southeast France landline",
                "5":"Southwest France landline",
                "8":"Special rate / Premium",
                "9":"VoIP / Internet telephony",
            }
            info("Line type", types.get(first, "Unknown"))

        print(Fore.CYAN + "\n  OSINT Links:")
        clean = "".join(c for c in number if c.isdigit() or c=="+")
        link(f"https://www.truecaller.com/search/us/{clean}")
        link(f"https://www.google.com/search?q=%22{number}%22")
        link(f"https://www.whocalledme.com/PhoneNumber/{clean}")
    else:
        warn("Unknown country prefix.")
    pause()

# ══════════════════════════════════════════════════════════════════
#  14 — METADATA EXTRACTOR (EXIF + GPS)
# ══════════════════════════════════════════════════════════════════

def _convert_gps(coord, ref):
    d, m, s = coord
    dd = d + m/60 + s/3600
    if ref in ("S","W"): dd = -dd
    return dd

def metadata_extractor():
    clear(); banner(); section("🔎  METADATA EXTRACTOR")
    if not PIL_OK:
        err("Pillow not installed."); warn("Run: pip install pillow"); pause(); return
    path = input(Fore.WHITE + "  Image path > ").strip().strip('"')
    try:
        img  = Image.open(path)
        exif = img.getexif()
        print()
        if not exif:
            warn("No EXIF metadata found."); pause(); return

        gps_data = {}
        for tag_id, val in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for k, v in val.items():
                    gps_data[GPSTAGS.get(k, k)] = v
            else:
                info(str(tag), str(val)[:80])

        if gps_data:
            print(Fore.CYAN + "\n  GPS Data:")
            for k, v in gps_data.items():
                info(str(k), str(v))
            try:
                lat = _convert_gps(gps_data["GPSLatitude"],  gps_data["GPSLatitudeRef"])
                lon = _convert_gps(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
                print(Fore.GREEN + f"\n  Coordinates: {lat:.6f}, {lon:.6f}")
                link(f"https://www.google.com/maps?q={lat},{lon}")
            except Exception: pass

    except FileNotFoundError:
        err("File not found.")
    except Exception as e:
        err(f"Error: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  15 — HASH GENERATOR
# ══════════════════════════════════════════════════════════════════

def hash_generator():
    clear(); banner(); section("🔐  HASH GENERATOR")
    text = input(Fore.WHITE + "  Text to hash > ").strip()
    if not text: pause(); return
    b = text.encode()
    print()
    info("MD5",    hashlib.md5(b).hexdigest())
    info("SHA1",   hashlib.sha1(b).hexdigest())
    info("SHA256", hashlib.sha256(b).hexdigest())
    info("SHA512", hashlib.sha512(b).hexdigest())
    info("SHA3-256",hashlib.sha3_256(b).hexdigest())
    # base64
    import base64
    info("Base64", base64.b64encode(b).decode())
    pause()

# ══════════════════════════════════════════════════════════════════
#  16 — HASH CRACKER
# ══════════════════════════════════════════════════════════════════

def hash_cracker():
    clear(); banner(); section("🔐  HASH CRACKER")
    target = input(Fore.WHITE + "  Hash > ").strip().lower()
    wordlist = input(Fore.WHITE + "  Wordlist path (blank = rockyou.txt) > ").strip()
    if not wordlist: wordlist = "/usr/share/wordlists/rockyou.txt"

    if not os.path.isfile(wordlist):
        err(f"Wordlist not found: {wordlist}"); pause(); return

    length_map = {
        32:  ("MD5",     hashlib.md5),
        40:  ("SHA1",    hashlib.sha1),
        64:  ("SHA256",  hashlib.sha256),
        128: ("SHA512",  hashlib.sha512),
        56:  ("SHA224",  hashlib.sha224),
    }
    detected = length_map.get(len(target))
    if not detected:
        err("Cannot detect hash type from length."); pause(); return

    algo_name, fn = detected
    print(Fore.YELLOW + f"\n  Detected: {algo_name}")
    print(Fore.YELLOW + "  Cracking...\n")
    start = time.time()
    try:
        with open(wordlist,"r",encoding="utf-8",errors="ignore") as f:
            for i, line in enumerate(f):
                word = line.strip()
                if fn(word.encode()).hexdigest() == target:
                    elapsed = time.time() - start
                    ok(f"CRACKED → {word}  (tried {i+1} words in {elapsed:.2f}s)")
                    pause(); return
                if i % 50000 == 0 and i > 0:
                    print(Fore.YELLOW + f"\r  {i:,} words tried...", end="", flush=True)
        err("Not found in wordlist.")
    except Exception as e:
        err(f"Error: {e}")
    pause()

# ══════════════════════════════════════════════════════════════════
#  17 — PASSWORD GENERATOR
# ══════════════════════════════════════════════════════════════════

def password_strength(pwd):
    score = 0
    checks = [
        (len(pwd) >= 8,  "At least 8 characters"),
        (len(pwd) >= 16, "At least 16 characters"),
        (any(c.islower() for c in pwd), "Lowercase letters"),
        (any(c.isupper() for c in pwd), "Uppercase letters"),
        (any(c.isdigit() for c in pwd), "Numbers"),
        (any(c in string.punctuation for c in pwd), "Special characters"),
    ]
    for passed, desc in checks:
        color = Fore.GREEN if passed else Fore.RED
        mark  = "✔" if passed else "✘"
        print(color + f"    [{mark}] {desc}")
        if passed: score += 1
    grades = {6:"Strong 💪",5:"Good",4:"Medium",3:"Weak",2:"Very Weak",1:"Terrible"}
    g = grades.get(score, "Terrible")
    color = Fore.GREEN if score>=5 else Fore.YELLOW if score>=3 else Fore.RED
    print(color + f"\n    Strength: {g} ({score}/6)")

def password_generator():
    clear(); banner(); section("🔐  PASSWORD GENERATOR")
    print(Fore.CYAN + "  (1) Generate password   (2) Test my password\n")
    c = input(Fore.WHITE + "  > ").strip()

    if c == "2":
        pwd = input(Fore.WHITE + "  Your password > ")
        print()
        password_strength(pwd)
        pause(); return

    try:
        length = int(input(Fore.WHITE + "  Length (default 20) > ").strip() or "20")
    except ValueError:
        length = 20

    print(Fore.CYAN + "\n  Include:")
    use_upper  = input("  Uppercase (Y/n)? ").strip().lower() != "n"
    use_digits = input("  Digits (Y/n)?    ").strip().lower() != "n"
    use_spec   = input("  Symbols (Y/n)?   ").strip().lower() != "n"

    charset = string.ascii_lowercase
    if use_upper:  charset += string.ascii_uppercase
    if use_digits: charset += string.digits
    if use_spec:   charset += string.punctuation

    print()
    for i in range(5):
        pwd = "".join(secrets.choice(charset) for _ in range(length))
        print(Fore.GREEN + f"  [{i+1}] {pwd}")

    print()
    password_strength("".join(secrets.choice(charset) for _ in range(length)))
    pause()

# ══════════════════════════════════════════════════════════════════
#  18 — CONTACT
# ══════════════════════════════════════════════════════════════════

def contact():
    clear(); banner(); section("🎭  CONTACT")
    print(Fore.CYAN + """
  ┌─────────────────────────────────┐
  │           camzzz                │
  │  Discord : cameleonmortis       │
  │  GitHub  : github.com/cameleonnbss │
  └─────────────────────────────────┘
""")
    pause()

# ══════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════

MENU_TEXT = """
{C}┌──────────── {Y}🌐 NETWORK{C} ────────────┐   {C}┌──────────── {Y}🔎 OSINT{C} ──────────────┐
{C}│ {G}01{W} IP Lookup & Tracker            {C}│   {C}│ {G}11{W} Username Tracker (50+)       {C}│
{C}│ {G}02{W} DNS Lookup (A/MX/NS/TXT...)   {C}│   {C}│ {G}12{W} Email OSINT                  {C}│
{C}│ {G}03{W} WHOIS Lookup                  {C}│   {C}│ {G}13{W} Phone Number Info            {C}│
{C}│ {G}04{W} Port Scanner                  {C}│   {C}│ {G}14{W} Metadata Extractor (GPS)     {C}│
{C}│ {G}05{W} Subdomain Finder (80+)        {C}│   {C}└─────────────────────────────────────┘
{C}│ {G}06{W} ASN / BGP Lookup              {C}│
{C}└──────────────────────────────────┘

{C}┌──────────── {Y}🌍 WEB{C} ─────────────┐   {C}┌──────────── {Y}🔐 HASH / PASSWORD{C} ───────┐
{C}│ {G}07{W} HTTP Header Inspector        {C}│   {C}│ {G}15{W} Hash Generator               {C}│
{C}│ {G}08{W} SSL Certificate Inspector    {C}│   {C}│ {G}16{W} Hash Cracker (wordlist)      {C}│
{C}│ {G}09{W} Tech Detector (30+ CMS)      {C}│   {C}│ {G}17{W} Password Generator + Tester {C}│
{C}│ {G}10{W} URL Redirect Tracer          {C}│   {C}└─────────────────────────────────────┘
{C}│ {G}10b{W} WAF Detector                {C}│
{C}└──────────────────────────────────┘   {C}┌──────────── {Y}🎭 EXTRA{C} ──────────────┐
                                          {C}│ {G}18{W} Contact                        {C}│
                                          {C}│ {G}00{W} Exit                           {C}│
                                          {C}└─────────────────────────────────────┘
"""

DISPATCH = {
    "01": ip_lookup,      "1":  ip_lookup,
    "02": dns_lookup,     "2":  dns_lookup,
    "03": whois_lookup,   "3":  whois_lookup,
    "04": port_scanner,   "4":  port_scanner,
    "05": subdomain_finder,"5": subdomain_finder,
    "06": asn_lookup,     "6":  asn_lookup,
    "07": http_headers,   "7":  http_headers,
    "08": ssl_inspector,  "8":  ssl_inspector,
    "09": tech_detector,  "9":  tech_detector,
    "10": redirect_tracer,
    "10b": waf_detector,
    "11": username_tracker,
    "12": email_osint,
    "13": phone_info,
    "14": metadata_extractor,
    "15": hash_generator,
    "16": hash_cracker,
    "17": password_generator,
    "18": contact,
}

if __name__ == "__main__":
    while True:
        clear()
        banner()
        print(MENU_TEXT.format(
            C=Fore.CYAN, Y=Fore.YELLOW,
            G=Fore.GREEN, W=Fore.WHITE
        ))
        choice = input(Fore.WHITE + "  Select module > ").strip().lower()
        if choice == "00" or choice == "exit" or choice == "q":
            print(Fore.GREEN + "\n  Goodbye!\n")
            break
        action = DISPATCH.get(choice)
        if action:
            action()
        else:
            err("Unknown module.")
            time.sleep(0.8)
