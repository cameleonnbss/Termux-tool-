#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════╗
#   CAMZZZ MULTI-TOOL V8 — TERMUX EDITION — By camzzz
#   100+ MODULES — OSINT / Network / Web / Breach / Hash / IA
#   Entièrement compatible Termux (Android) + Linux + Windows
#   github.com/cameleonnbss
# ╚══════════════════════════════════════════════════════════════════╝
#
#  INSTALL (Termux) :
#    pkg update && pkg upgrade -y
#    pkg install python python-pip git -y
#    pip install requests colorama Pillow
#    python camzzz-v8-termux.py
#
#  OUTILS OPEN SOURCE (optionnels) :
#    pip install holehe sherlock-project maigret h8mail theHarvester
#
#  NOTES TERMUX :
#    - Traceroute raw socket : utilise ping fallback (pas besoin de root)
#    - WiFi scanner : utilise termux-wifi-scaninfo (pkg install termux-api)
#    - Tout le reste fonctionne nativement sans root

import os, sys, platform, socket, ssl, re, hashlib, base64
import time, random, string, urllib.parse, subprocess, configparser, json
import concurrent.futures, ipaddress, secrets
from datetime import datetime

# ══════════════════════════════════════════════
#  AUTO-INSTALL DES DEPENDANCES
# ══════════════════════════════════════════════

def _ensure_deps():
    import importlib.util, subprocess as _sp
    deps = {"requests": "requests", "colorama": "colorama"}
    missing = [pkg for mod, pkg in deps.items() if not importlib.util.find_spec(mod)]
    if missing:
        print(f"  [*] Installation des dépendances: {', '.join(missing)}")
        _sp.check_call([sys.executable, "-m", "pip", "install"] + missing,
                       stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        print("  [OK] Dépendances installées.\n")
_ensure_deps()

import requests
from colorama import Fore, Style, init
init(autoreset=True)

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_OK = True
except ImportError:
    PIL_OK = False; Image = None; TAGS = {}; GPSTAGS = {}

# ══════════════════════════════════════════════
#  DETECTION ENVIRONNEMENT
# ══════════════════════════════════════════════

SYS       = platform.system().lower()
IS_WIN    = sys.platform == "win32"
IS_TERMUX = os.path.isdir("/data/data/com.termux") and not IS_WIN
IS_LINUX  = SYS == "linux" and not IS_TERMUX

# ══════════════════════════════════════════════
#  CONFIG API KEYS (config.ini)
# ══════════════════════════════════════════════

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
CONFIG_TEMPLATE = """\
# CAMZZZ MULTI-TOOL V8 — Config API Keys
# Remplis tes clés ici — chargées automatiquement au lancement

[API_KEYS]
# LeakCheck — Free 50 req/mois — https://leakcheck.io
leakcheck_key =
# BreachDirectory via RapidAPI — https://rapidapi.com/rohan-patra/api/breachdirectory
breachdirectory_key =
# Shodan — https://account.shodan.io/register
shodan_key =
# Hunter.io — https://hunter.io
hunter_key =
# VirusTotal — https://www.virustotal.com
virustotal_key =
# OpenRouter IA (gratuit) — https://openrouter.ai
openrouter_key =

[SETTINGS]
timeout = 10
show_intro = true
lang = fr
"""

def load_config():
    cfg = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(CONFIG_TEMPLATE)
        print(f"\033[93m  [CONFIG] Fichier config.ini créé: {CONFIG_FILE}\033[0m\n")
        time.sleep(1)
    cfg.read(CONFIG_FILE, encoding="utf-8")
    return cfg

def get_key(cfg, name, fallback=""):
    try:
        val = cfg.get("API_KEYS", name, fallback=fallback).strip()
        return val if val else fallback
    except Exception: return fallback

def save_key(name, value):
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE, encoding="utf-8")
    if not cfg.has_section("API_KEYS"): cfg.add_section("API_KEYS")
    cfg.set("API_KEYS", name, value)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)

def get_setting(cfg, name, fallback=""):
    try: return cfg.get("SETTINGS", name, fallback=fallback).strip()
    except Exception: return fallback

_CFG          = load_config()
LEAKCHECK_KEY  = get_key(_CFG, "leakcheck_key")
BREACHDIR_KEY  = get_key(_CFG, "breachdirectory_key")
SHODAN_KEY     = get_key(_CFG, "shodan_key")
HUNTER_KEY     = get_key(_CFG, "hunter_key")
VIRUSTOTAL_KEY = get_key(_CFG, "virustotal_key")
OPENROUTER_KEY = get_key(_CFG, "openrouter_key")
REQ_TIMEOUT    = int(get_setting(_CFG, "timeout", "10"))
SHOW_INTRO     = get_setting(_CFG, "show_intro", "true").lower() == "true"

# ══════════════════════════════════════════════
#  COULEURS
# ══════════════════════════════════════════════

G=Fore.GREEN;   LG=Fore.LIGHTGREEN_EX
Y=Fore.YELLOW;  LY=Fore.LIGHTYELLOW_EX
C=Fore.CYAN;    LC=Fore.LIGHTCYAN_EX
R=Fore.RED;     LR=Fore.LIGHTRED_EX
M=Fore.MAGENTA; LM=Fore.LIGHTMAGENTA_EX
W=Fore.WHITE;   LW=Fore.LIGHTWHITE_EX
DIM=Style.DIM

# ══════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════

def clear():
    os.system("cls" if IS_WIN else "clear")

def pause():
    print()
    input(LG + "  ╔══════════════════════════════════╗\n"
               "  ║  ENTER pour revenir au menu     ║\n"
               "  ╚══════════════════════════════════╝  ")

def row(l, v, lc=C, vc=LW):
    print(lc + f"  {str(l):<28}" + vc + f" {str(v)[:72]}")

def section(t, col=LG):
    w=54; pad=(w-len(t)-2)//2; ex=w-pad-len(t)-2
    print(); print(col + f"  ╔{'═'*w}╗")
    print(col + f"  ║{' '*pad} {t} {' '*max(0,ex)}║")
    print(col + f"  ╚{'═'*w}╝"); print()

def ok(msg):   print(LG + f"  [✔] {msg}")
def warn(msg): print(LY + f"  [!] {msg}")
def err(msg):  print(LR + f"  [✘] {msg}")
def lnk(name, url, col=LC):
    print(col + f"  {name:<28}" + LW + f" {url}")

def spinner(label, dur=1.0, col=LG):
    frames = ["-", "\\", "|", "/"]
    end = time.time() + dur; i = 0
    while time.time() < end:
        sys.stdout.write(col + f"\r  {frames[i%4]}  {label}   ")
        sys.stdout.flush(); time.sleep(0.1); i += 1
    sys.stdout.write("\r" + " "*72 + "\r"); sys.stdout.flush()

def bar(label, steps=30, delay=0.018, col=LG, bc=G):
    for i in range(steps+1):
        f = "#"*i + "."*(steps-i); pct = int(i/steps*100)
        sys.stdout.write(col + f"\r  {label}  " + bc + f"[{f}]" + LW + f" {pct:3d}%")
        sys.stdout.flush(); time.sleep(delay)
    print()

def glitch(text, rounds=3, col=LG):
    noise = "@#$%&?!*~^<>|"
    for _ in range(rounds):
        g = "".join(random.choice(noise) if random.random()<0.25 else ch for ch in text)
        sys.stdout.write("\r"+col+g); sys.stdout.flush(); time.sleep(0.06)
    sys.stdout.write("\r"+col+text+"\n"); sys.stdout.flush()

def rainbow(text):
    cols=[LR,Y,LG,LC,LM,LW,LY,LC]
    print("".join(cols[i%len(cols)]+ch for i,ch in enumerate(text)))

def qenc(q): return urllib.parse.quote(str(q))

REQ_HDR = {"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"}

def rget(url, timeout=None, **kw):
    return requests.get(url, headers=REQ_HDR, timeout=timeout or REQ_TIMEOUT, **kw)

# ══════════════════════════════════════════════
#  BANNER / INTRO
# ══════════════════════════════════════════════

CAMZZZ_LINES = [
    "   ██████╗ █████╗ ███╗   ███╗███████╗███████╗███████╗",
    "  ██╔════╝██╔══██╗████╗ ████║╚══███╔╝╚══███╔╝╚══███╔╝",
    "  ██║     ███████║██╔████╔██║  ███╔╝   ███╔╝   ███╔╝ ",
    "  ██║     ██╔══██║██║╚██╔╝██║ ███╔╝   ███╔╝   ███╔╝  ",
    "  ╚██████╗██║  ██║██║ ╚═╝ ██║███████╗███████╗███████╗",
    "   ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝",
]

def banner():
    clear()
    for line in CAMZZZ_LINES: rainbow(line)
    print()
    print(C + "  " + "─"*62)
    env = "TERMUX" if IS_TERMUX else ("WINDOWS" if IS_WIN else "LINUX")
    print(C + f"  V8 TERMUX EDITION  │  By camzzz  │  {env}  │  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(C + f"  github.com/cameleonnbss  │  Discord: cameleonmortis")
    print(C + "  " + "─"*62)
    print()

def intro():
    if not SHOW_INTRO: return
    clear()
    boot = [
        "  [          ]  BOOTING V8...",
        "  [###       ]  LOADING MODULES...",
        "  [######    ]  TERMUX OPTIMIZED...",
        "  [#########]  NETWORK READY...",
        "  [##########]  ACCESS GRANTED — V8 — 100+ MODULES",
    ]
    for frame in boot:
        clear(); print(LG + "\n" + frame); time.sleep(0.3)
    time.sleep(0.2); clear()
    print(LG + "\n  " + "="*62)
    glitch("     C A M Z Z Z   V 8   —   T E R M U X   E D I T I O N", 3, LG)
    print(LG + "  " + "="*62 + "\n")
    for line in CAMZZZ_LINES: rainbow(line); time.sleep(0.04)
    print()
    input(LG + "  >>> PRESS ENTER TO CONTINUE <<<  ")
    clear()

# ══════════════════════════════════════════════
#  01 — IP INFO & TRACKER
# ══════════════════════════════════════════════

def ip_info():
    banner()
    section("IP INFO & TRACKER", LG)
    print(LW + "  1  Mon IP publique\n  2  Lookup n'importe quelle IP\n  3  Liens réputation IP\n  4  Scanner range /24")
    c = input(LG + "\n  Choix > ").strip()

    if c == "1":
        spinner("Récupération de ton IP...", 1.0, LG)
        try:
            ip = requests.get("https://api.ipify.org?format=json", timeout=8).json().get("ip","?")
            geo = rget(f"https://ipapi.co/{ip}/json").json()
            section(f"TON IP: {ip}", LG)
            for f in ["ip","country_name","region","city","postal","org","asn","timezone","latitude","longitude"]:
                v = geo.get(f)
                if v: row(f, v)
            lat,lon = geo.get("latitude",""),geo.get("longitude","")
            if lat and lon: print(); lnk("Google Maps", f"https://maps.google.com/?q={lat},{lon}", LG)
        except Exception as e: err(f"Erreur: {e}")

    elif c == "2":
        ip = input(LG + "  IP > ").strip()
        if not ip: pause(); return
        spinner(f"Lookup {ip}...", 1.0, LG)
        try:
            geo  = rget(f"https://ipapi.co/{ip}/json").json()
            geo2 = rget(f"http://ip-api.com/json/{ip}").json()
            section(f"IP INFO — {ip}", LG)
            for f in ["country_name","region","city","postal","latitude","longitude","timezone","org","asn","currency","languages","network"]:
                v = geo.get(f) or geo2.get(f)
                if v and v != "N/A": row(f, v)
            lat,lon = geo.get("latitude",""),geo.get("longitude","")
            if lat and lon: lnk("Google Maps", f"https://maps.google.com/?q={lat},{lon}", LG)
            section("LIENS RÉPUTATION", LG)
            for name,url in [
                ("VirusTotal",  f"https://www.virustotal.com/gui/ip-address/{ip}"),
                ("AbuseIPDB",   f"https://www.abuseipdb.com/check/{ip}"),
                ("Shodan",      f"https://www.shodan.io/host/{ip}"),
                ("Greynoise",   f"https://viz.greynoise.io/ip/{ip}"),
                ("Censys",      f"https://search.censys.io/hosts/{ip}"),
                ("OTX",         f"https://otx.alienvault.com/indicator/ip/{ip}"),
                ("Talos",       f"https://talosintelligence.com/reputation_center/lookup?search={ip}"),
                ("IPQualityScore",f"https://www.ipqualityscore.com/ip-reputation/proxy-vpn-bot-check/{ip}"),
            ]: lnk(name, url)
        except Exception as e: err(f"Erreur: {e}")

    elif c == "3":
        ip = input(LG + "  IP > ").strip()
        section("FULL REPUTATION LINKS", LG)
        for name,url in [
            ("AbuseIPDB",    f"https://www.abuseipdb.com/check/{ip}"),
            ("VirusTotal",   f"https://www.virustotal.com/gui/ip-address/{ip}"),
            ("Shodan",       f"https://www.shodan.io/host/{ip}"),
            ("Greynoise",    f"https://viz.greynoise.io/ip/{ip}"),
            ("Censys",       f"https://search.censys.io/hosts/{ip}"),
            ("IPVoid",       f"https://www.ipvoid.com/ip-blacklist-check/?ip={ip}"),
            ("Spamhaus",     f"https://check.spamhaus.org/query/ip/{ip}"),
            ("MXToolbox",    f"https://mxtoolbox.com/SuperTool.aspx?action=blacklist%3a{ip}"),
        ]: lnk(name, url)

    elif c == "4":
        base = input(LG + "  IP de base (ex: 192.168.1) > ").strip()
        section(f"IP RANGE SCANNER — {base}.0/24", LG)
        found = []
        spinner("Scan en cours...", 0.5, LG)
        def chk(i):
            ip2 = f"{base}.{i}"
            try:
                s = socket.socket(); s.settimeout(0.4)
                if s.connect_ex((ip2, 80)) == 0: s.close(); return ip2
                s.close()
            except: return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
            results = list(ex.map(chk, range(1,255)))
        for r in [r for r in results if r]:
            found.append(r); print(LG + f"  [+]  {r}")
        print(LG + f"\n  {len(found)} hôte(s) trouvé(s).")
    pause()

# ══════════════════════════════════════════════
#  02 — DNS LOOKUP
# ══════════════════════════════════════════════

DNS_TYPES = ["A","AAAA","MX","NS","TXT","CNAME","SOA","CAA","SRV","PTR"]

def dns_lookup():
    banner(); section("DNS LOOKUP", LC)
    domain = input(LW + "  Domaine > ").strip()
    if not domain: pause(); return
    spinner(f"Requête DNS pour {domain}...", 1.0, LC)
    results = {}
    for rtype in DNS_TYPES:
        try:
            r = rget(f"https://dns.google/resolve?name={domain}&type={rtype}", timeout=6).json()
            answers = r.get("Answer", [])
            if answers:
                results[rtype] = [a.get("data","") for a in answers]
        except Exception: pass
    print()
    if not results: err("Aucun enregistrement DNS trouvé.")
    else:
        for rtype, values in results.items():
            for v in values: row(rtype, v, LC)
    a_recs = results.get("A",[])
    if a_recs:
        try:
            rev = socket.gethostbyaddr(a_recs[0])
            row("Reverse (PTR)", rev[0], LC)
        except: pass
    section("LIENS DNS/WHOIS", LC)
    e = qenc(domain)
    for name,url in [
        ("MXToolbox",     f"https://mxtoolbox.com/SuperTool.aspx?action=mx%3a{e}"),
        ("DNSdumpster",   f"https://dnsdumpster.com/ [{domain}]"),
        ("SecurityTrails",f"https://securitytrails.com/domain/{domain}/dns"),
        ("ViewDNS",       f"https://viewdns.info/dnsreport/?domain={domain}"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  03 — WHOIS / REVERSE DNS
# ══════════════════════════════════════════════

def whois_reverse():
    banner(); section("WHOIS / REVERSE DNS", LY)
    print(LW + "  1  WHOIS domaine\n  2  Reverse DNS (IP → hostname)\n  3  WHOIS IP\n")
    c = input(LY + "  Choix > ").strip()

    if c == "1":
        d = input(LY + "  Domaine > ").strip()
        spinner("Requête WHOIS...", 1.0, LY)
        try:
            r = rget(f"https://api.whois.vu/?q={d}", timeout=10).json()
            section("WHOIS DATA", LY)
            for k,v in r.items():
                if v: row(k, v, LY)
        except:
            try: row("IP résolu", socket.gethostbyname(d), LY)
            except: pass
        section("LIENS WHOIS", LY)
        for name,url in [
            ("ICANN",     f"https://lookup.icann.org/en/lookup?name={d}"),
            ("Whois.com", f"https://www.whois.com/whois/{d}"),
            ("DomainTools",f"https://whois.domaintools.com/{d}"),
            ("RDAP IANA", f"https://rdap.iana.org/domain/{d}"),
        ]: lnk(name, url)

    elif c == "2":
        ip = input(LY + "  IP > ").strip()
        spinner("Reverse DNS...", 0.8, LY)
        try:
            h = socket.gethostbyaddr(ip)
            section("REVERSE DNS", LY)
            row("IP", ip, LY); row("Hostname", h[0], LY, LG)
            if len(h[1]) > 0: row("Aliases", ", ".join(h[1]), LY)
        except Exception as e: err(f"Échec: {e}")

    elif c == "3":
        ip = input(LY + "  IP > ").strip()
        spinner("WHOIS IP...", 1.0, LY)
        try:
            r = rget(f"https://ipapi.co/{ip}/json").json()
            section(f"WHOIS IP — {ip}", LY)
            for f in ["org","asn","network","country_name","region","city","postal"]:
                v = r.get(f)
                if v: row(f, v, LY)
        except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  04 — PORT SCANNER
# ══════════════════════════════════════════════

COMMON_PORTS = {
    20:"FTP-data",21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",
    80:"HTTP",110:"POP3",119:"NNTP",123:"NTP",135:"MSRPC",137:"NetBIOS",
    139:"NetBIOS",143:"IMAP",194:"IRC",443:"HTTPS",445:"SMB",
    3306:"MySQL",3389:"RDP",5432:"PostgreSQL",5900:"VNC",
    6379:"Redis",8080:"HTTP-alt",8443:"HTTPS-alt",8888:"HTTP-dev",
    27017:"MongoDB",9200:"Elasticsearch",6667:"IRC",
}

def port_scanner():
    banner(); section("PORT SCANNER", LG)
    host = input(LW + "  Host/IP > ").strip()
    if not host: pause(); return
    print(LW + "  1  Top ports courants (~30)\n  2  Ports personnalisés\n  3  Scan rapide 1-1024\n")
    c = input(LG + "  Choix > ").strip()

    if c == "1":
        ports = list(COMMON_PORTS.keys())
    elif c == "2":
        raw = input(LW + "  Ports (ex: 22,80,443,8080) > ").strip()
        try: ports = [int(p.strip()) for p in raw.split(",") if p.strip()]
        except: err("Format invalide."); pause(); return
    else:
        ports = list(range(1, 1025))

    try: target_ip = socket.gethostbyname(host)
    except: err(f"DNS résolution échouée."); pause(); return

    section(f"SCAN — {host} ({target_ip}) — {len(ports)} ports", LG)
    print(LG + f"  {'PORT':<8} {'SERVICE':<18} {'ETAT':<8} {'BANNER'}")
    print(LG + "  " + "─"*62)

    open_ports = []
    def scan_port(port):
        try:
            s = socket.socket(); s.settimeout(0.6)
            res = s.connect_ex((target_ip, port))
            if res == 0:
                banner_txt = ""
                try:
                    if port in [80,8080,8000,8888]:
                        s.sendall(f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
                        banner_txt = s.recv(256).decode(errors="replace").split("\n")[0][:40]
                    else:
                        s.settimeout(0.4)
                        banner_txt = s.recv(256).decode(errors="replace").strip()[:40]
                except: pass
                s.close()
                return (port, True, banner_txt)
            s.close()
        except: pass
        return (port, False, "")

    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as ex:
        results = sorted(ex.map(scan_port, ports), key=lambda x: x[0])

    for port, is_open, bnr in results:
        svc = COMMON_PORTS.get(port, "unknown")
        if is_open:
            open_ports.append(port)
            print(LG + f"  {port:<8} {svc:<18} OUVERT   {bnr}")
        elif c == "2":
            print(DIM+LW + f"  {port:<8} {svc:<18} fermé")

    print(LG + f"\n  {len(open_ports)} port(s) ouvert(s) trouvé(s).")
    pause()

# ══════════════════════════════════════════════
#  05 — SUBDOMAIN FINDER
# ══════════════════════════════════════════════

SUBS = [
    "www","mail","ftp","smtp","pop","imap","webmail","cpanel","admin","api",
    "dev","staging","test","beta","app","portal","dashboard","blog","shop",
    "store","forum","support","help","docs","cdn","static","media","img",
    "images","video","files","download","upload","auth","login","secure","vpn",
    "ssh","git","gitlab","jenkins","ci","status","monitor","grafana","ns1","ns2",
    "mx","mx1","mx2","remote","owa","exchange","autodiscover","m","mobile","panel",
    "server","host","cloud","backup","old","new","v1","v2","api2","search","news",
    "web","assets","s3","bucket","data","db","database","internal","intranet",
    "extranet","private","public","corp","crm","erp","vpn2","proxy","gateway",
    "relay","sftp","ntp","ldap","jira","confluence","wiki","redmine","phpmyadmin",
    "mysql","postgres","elastic","kibana","prometheus","nagios","zabbix","splunk",
    "demo","pre","preprod","uat","qa","prod","production","smtp2","pop3","imap4",
    "mail2","ssl","email","assets2","cdn2","api3","graphql","rest","rpc","grpc",
    "office","vpn3","dev2","test2","stage","shop2","app2","frontend","backend",
    "api4","forum2","news2","old2","legacy","wordpress","wp","blog2","cms",
]

def subdomain_finder():
    banner(); section("SUBDOMAIN FINDER", LC)
    domain = input(LC + "  Domaine > ").strip()
    if not domain: pause(); return
    bar("  Construction wordlist", 20, 0.012, LC, C)
    print(LC + f"\n  Test de {len(SUBS)} sous-domaines sur {domain}...\n")
    found = []

    def chk(sub):
        t = f"{sub}.{domain}"
        try: return (t, socket.gethostbyname(t))
        except: return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        results = list(ex.map(chk, SUBS))

    section("SOUS-DOMAINES TROUVÉS", LC)
    for r in [r for r in results if r]:
        sub, ip = r; found.append(sub)
        print(LC + f"  [+]  {sub:<48}" + LW + f" → {ip}")
    print(LC + f"\n  {len(found)} sous-domaine(s) trouvé(s).")
    section("RECHERCHE PASSIVE", LC)
    e = qenc(domain)
    for name,url in [
        ("crt.sh",        f"https://crt.sh/?q=%.{domain}"),
        ("Shodan",        f"https://www.shodan.io/domain/{domain}"),
        ("URLScan",       f"https://urlscan.io/search/#{e}"),
        ("VirusTotal",    f"https://www.virustotal.com/gui/domain/{domain}/relations"),
        ("SecurityTrails",f"https://securitytrails.com/domain/{domain}/subdomains"),
        ("Censys",        f"https://search.censys.io/search?resource=hosts&q={e}"),
        ("DNSdumpster",   f"https://dnsdumpster.com/ [{domain}]"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  06 — ASN / BGP LOOKUP
# ══════════════════════════════════════════════

def asn_lookup():
    banner(); section("ASN / BGP LOOKUP", LC)
    target = input(LW + "  IP, domaine ou ASN (ex: AS15169) > ").strip()
    if not target: pause(); return
    spinner("Requête BGP...", 1.0, LC)

    if target.upper().startswith("AS"):
        asn = target.upper().replace("AS","")
        try:
            r = rget(f"https://api.bgpview.io/asn/{asn}", timeout=10).json()
            data = r.get("data", {})
            section(f"ASN INFO — AS{asn}", LC)
            row("ASN",     f"AS{data.get('asn','?')}", LC)
            row("Name",    data.get("name","?"), LC)
            row("Country", data.get("country_code","?"), LC)
            row("Org",     data.get("description_short","?"), LC)
            peers = data.get("rir_allocation", {})
            if peers: row("RIR", peers.get("rir_name","?"), LC)
        except Exception as e: err(f"Erreur: {e}")
    else:
        try:
            ip = socket.gethostbyname(target)
            r = rget(f"https://api.bgpview.io/ip/{ip}", timeout=10).json()
            data = r.get("data", {})
            section(f"BGP INFO — {ip}", LC)
            pfxs = data.get("prefixes", [])
            if pfxs:
                pfx = pfxs[0]
                row("Prefix", pfx.get("prefix","?"), LC)
                row("ASN",    f"AS{pfx.get('asn',{}).get('asn','?')}", LC)
                row("Name",   pfx.get("asn",{}).get("name","?"), LC)
                row("Country",pfx.get("country_code","?"), LC)
                row("RIR",    pfx.get("rir_allocation",{}).get("rir_name","?"), LC)
        except Exception as e: err(f"Erreur: {e}")

    section("LIENS ASN/BGP", LC)
    e = qenc(target)
    for name,url in [
        ("BGPView",    f"https://bgpview.io/search#{e}"),
        ("Hurricane Electric",f"https://bgp.he.net/search?search%5Bsearch%5D={e}"),
        ("RIPE NCC",   f"https://apps.db.ripe.net/db-web-ui/query?searchtext={e}"),
        ("ASNlookup",  f"https://asnlookup.com/asn/{e}"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  07 — HTTP HEADER INSPECTOR
# ══════════════════════════════════════════════

def header_inspector():
    banner(); section("HTTP HEADER INSPECTOR", LC)
    url = input(LC + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    spinner("Récupération des headers...", 0.8, LC)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        section("RESPONSE HEADERS", LC)
        for k,v in r.headers.items(): row(k, v, LC)
        section("AUDIT SÉCURITÉ HEADERS", LC)
        sec = {
            "Strict-Transport-Security": ("HSTS", LG),
            "Content-Security-Policy":   ("CSP",  LG),
            "X-Frame-Options":           ("Clickjacking protection", LY),
            "X-Content-Type-Options":    ("MIME sniff protection", LY),
            "Referrer-Policy":           ("Referrer policy", LY),
            "Permissions-Policy":        ("Feature policy", LY),
            "X-XSS-Protection":          ("XSS filter (legacy)", DIM+LW),
        }
        for h,(desc,col) in sec.items():
            v = r.headers.get(h)
            flag = LG + "  [OK      ] " if v else LR + "  [MANQUANT] "
            print(flag + LW + f"{h:<38} " + col + desc)
        section("INFOS SERVEUR", LC)
        row("Status", str(r.status_code), LC)
        row("Server", r.headers.get("Server","N/A"), LC)
        row("X-Powered-By", r.headers.get("X-Powered-By","N/A"), LC)
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  08 — SSL CERTIFICATE INSPECTOR
# ══════════════════════════════════════════════

def ssl_inspector():
    banner(); section("SSL CERTIFICATE INSPECTOR", LC)
    host = input(LC + "  Hôte > ").strip()
    if not host: pause(); return
    spinner("Connexion SSL...", 1.0, LC)
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(10); s.connect((host, 443))
            cert = s.getpeercert(); proto = s.version(); cipher = s.cipher()
        subj = dict(x[0] for x in cert.get("subject",[]))
        iss  = dict(x[0] for x in cert.get("issuer",[]))
        section("CERTIFICAT SSL", LC)
        row("CN Sujet",   subj.get("commonName","N/A"), LC)
        row("Org",        subj.get("organizationName","N/A"), LC)
        row("Émetteur",   iss.get("organizationName","N/A"), LC)
        row("Valide du",  cert.get("notBefore","N/A"), LC, LG)
        row("Valide au",  cert.get("notAfter","N/A"),  LC, LG)
        row("Protocole",  proto or "N/A", LC)
        row("Cipher",     cipher[0] if cipher else "N/A", LC)
        sans = cert.get("subjectAltName",[])
        if sans:
            section("SUBJECT ALT NAMES", LC)
            for t,v in sans: print(LC + f"  {t:<10}" + LW + f" {v}")
        # Expiration check
        try:
            exp = datetime.strptime(cert.get("notAfter",""), "%b %d %H:%M:%S %Y %Z")
            days = (exp - datetime.utcnow()).days
            col = LG if days > 30 else LY if days > 7 else LR
            row("Expire dans", f"{days} jours", LC, col)
        except: pass
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  09 — TECH DETECTOR
# ══════════════════════════════════════════════

def tech_detector():
    banner(); section("TECHNOLOGY DETECTOR", LY)
    url = input(LY + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    spinner("Analyse du site...", 1.2, LY)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=True)
        body = r.text.lower(); hdrs = str(r.headers).lower(); cookies = str(r.cookies).lower()
        checks = {
            "WordPress":  ["wp-content","wp-includes","wp-json"],
            "Drupal":     ["drupal","sites/default"],
            "Joomla":     ["joomla","option=com_"],
            "Shopify":    ["shopify","cdn.shopify.com"],
            "Wix":        ["wix.com","wixstatic.com"],
            "Squarespace":["squarespace.com"],
            "Ghost":      ["ghost.io","content/themes"],
            "React":      ["react","__react","reactdom"],
            "Vue.js":     ["vue.js","vue.min.js","__vue"],
            "Angular":    ["angular","ng-version"],
            "Next.js":    ["__next","_next/static"],
            "Nuxt.js":    ["__nuxt","_nuxt"],
            "jQuery":     ["jquery","jquery.min.js"],
            "Bootstrap":  ["bootstrap.min","bootstrap.css"],
            "Tailwind":   ["tailwindcss","tailwind"],
            "PHP":        [".php","x-powered-by: php"],
            "Django":     ["csrfmiddlewaretoken","django"],
            "Laravel":    ["laravel_session","laravel"],
            "Ruby on Rails":["rails","csrf-token"],
            "ASP.NET":    ["asp.net","__viewstate","aspnetcore"],
            "Cloudflare": ["cf-ray","cloudflare"],
            "Nginx":      ["nginx"],
            "Apache":     ["apache"],
            "Google Analytics":["gtag(","google-analytics","ga.js"],
            "Google Tag Manager":["googletagmanager.com"],
            "Matomo":     ["matomo.php","piwik.php"],
            "Stripe":     ["stripe.com","js.stripe.com"],
            "Intercom":   ["intercom","widget.intercom.io"],
            "HubSpot":    ["hubspot","hs-scripts"],
        }
        section("TECHNOLOGIES DÉTECTÉES", LY)
        found = []
        for tech, sigs in checks.items():
            for sig in sigs:
                if sig in body or sig in hdrs or sig in cookies:
                    found.append(tech); break
        if found:
            for t in found: print(LY + f"  [+]  {t}")
        else: print(LY + "  Rien de détecté clairement.")
        section("INFOS SERVEUR", LY)
        row("Server",       r.headers.get("Server","N/A"), LY)
        row("X-Powered-By", r.headers.get("X-Powered-By","N/A"), LY)
        row("Status",       str(r.status_code), LY)
        row("URL finale",   r.url[:70], LY)
        row("Taille",       f"{len(r.content):,} bytes", LY)
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  10 — URL REDIRECT TRACER
# ══════════════════════════════════════════════

def url_tracer():
    banner(); section("URL REDIRECT TRACER", LG)
    url = input(LG + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    spinner("Trace des redirections...", 0.8, LG)
    try:
        r = requests.get(url, timeout=10, allow_redirects=True, headers={"User-Agent":"Mozilla/5.0"})
        section("CHAÎNE DE REDIRECTIONS", LG)
        for i, resp in enumerate(r.history + [r]):
            col = LY if resp.status_code in [301,302,307,308] else LG
            print(col + f"  Étape {i}  [{resp.status_code}]  {resp.url}")
        print(LG + f"\n  {len(r.history)} redirection(s) — URL finale: {r.url}")
        row("Server final",  r.headers.get("Server","N/A"), LG)
        row("Content-Type",  r.headers.get("Content-Type","N/A"), LG)
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  11 — WAF / FIREWALL DETECTOR
# ══════════════════════════════════════════════

def waf_detector():
    banner(); section("WAF / FIREWALL DETECTOR", LR)
    url = input(LR + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    spinner("Analyse WAF...", 1.2, LR)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        hdrs = {k.lower(): v.lower() for k,v in r.headers.items()}
        body = r.text.lower()
        waf_sigs = {
            "Cloudflare":     ["cf-ray", "cloudflare"],
            "AWS WAF":        ["x-amzn-requestid","awswaf"],
            "Akamai":         ["x-akamai","akamaighost"],
            "Sucuri":         ["x-sucuri-id","sucuri-cloudproxy"],
            "Imperva Incapsula":["x-iinfo","incapsula"],
            "F5 BIG-IP":      ["x-wa-info","bigip"],
            "ModSecurity":    ["mod_security","modsecurity"],
            "Barracuda":      ["barra_counter_session"],
            "DenyAll":        ["denyall"],
        }
        section("DÉTECTION WAF", LR)
        detected = []
        for waf, sigs in waf_sigs.items():
            for sig in sigs:
                if any(sig in v for v in hdrs.values()) or sig in body:
                    detected.append(waf); break
        if detected:
            for w in detected: print(LR + f"  [!]  WAF Détecté: {w}")
        else:
            print(LY + "  Aucun WAF connu détecté (pourrait être custom ou absent).")
        section("HEADERS LIÉS SÉCURITÉ", LR)
        for h in ["server","x-powered-by","x-frame-options","cf-ray","x-cache"]:
            if h in hdrs: row(h, hdrs[h], LR)
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  12 — TRACEROUTE (Termux-compatible)
# ══════════════════════════════════════════════

def traceroute():
    banner(); section("TRACEROUTE", LY)
    host = input(LY + "  Hôte/IP > ").strip()
    if not host: pause(); return
    try: dest_ip = socket.gethostbyname(host)
    except Exception as e: err(f"DNS échoué: {e}"); pause(); return

    section(f"TRACEROUTE — {host} ({dest_ip})", LY)

    # Windows: tracert natif
    if IS_WIN:
        subprocess.run(["tracert", "-d", "-h", "30", host], timeout=60)
        pause(); return

    # Termux/Linux: essai via ping TTL (pas besoin de root)
    print(LY + f"  {'HOP':<5} {'IP':<22} {'RTT':<12} {'HOSTNAME'}")
    print(LY + "  " + "─"*60)

    for ttl in range(1, 31):
        try:
            cmd = ["ping", "-c", "1", "-W", "2", "-t" if IS_TERMUX or sys.platform=="darwin" else "-T",
                   str(ttl), dest_ip]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            rtt_m = re.search(r"time=([\d.]+)", result.stdout)
            rtt = f"{float(rtt_m.group(1)):.1f}ms" if rtt_m else "*"

            # Extraire l'IP du ping
            ip_m = re.search(r"from ([\d.]+)", result.stderr + result.stdout)
            recv_ip = ip_m.group(1) if ip_m else "*"

            hostname = "?"
            if recv_ip not in ["*","?"]:
                try: hostname = socket.gethostbyaddr(recv_ip)[0]
                except: hostname = recv_ip

            col = LG if recv_ip == dest_ip else LY if recv_ip != "*" else DIM+LW
            print(col + f"  {ttl:<5} {str(recv_ip):<22} {rtt:<12} {hostname}")
            if recv_ip == dest_ip:
                print(LG + f"\n  Destination atteinte en {ttl} sauts.")
                break
        except Exception:
            print(DIM+LW + f"  {ttl:<5} {'*':<22} {'*':<12} ?")
    pause()

# ══════════════════════════════════════════════
#  13 — BANNER GRABBER
# ══════════════════════════════════════════════

def banner_grab():
    banner(); section("BANNER GRABBER", LG)
    host = input(LG + "  Hôte/IP > ").strip()
    if not host: pause(); return
    ports_raw = input(LG + "  Ports (ex: 21,22,80,443,8080) > ").strip()
    try: ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip()]
    except: err("Format invalide."); pause(); return

    section(f"BANNERS — {host}", LG)
    for port in ports:
        try:
            s = socket.socket(); s.settimeout(3)
            s.connect((host, port))
            if port in [80, 8080, 8000, 8888]:
                s.sendall(f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
            elif port == 443:
                s.close()
                ctx = ssl.create_default_context()
                ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(socket.socket(), server_hostname=host)
                s.settimeout(3); s.connect((host, 443))
                s.sendall(f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
            bnr = s.recv(1024).decode(errors="replace").strip()[:300]
            s.close()
            print(LG + f"\n  Port {port}:")
            for line in bnr.split("\n")[:6]: print(LW + f"    {line.strip()}")
        except ConnectionRefusedError: print(DIM+LW + f"  Port {port}: Fermé")
        except Exception as e: print(LY + f"  Port {port}: {e}")
    pause()

# ══════════════════════════════════════════════
#  14 — MAC VENDOR LOOKUP
# ══════════════════════════════════════════════

def mac_lookup():
    banner(); section("MAC VENDOR LOOKUP", LY)
    mac = input(LY + "  Adresse MAC (ex: 00:1A:2B:3C:4D:5E) > ").strip()
    if not mac: pause(); return
    mac_clean = mac.upper().replace("-",":").replace(".",":")
    oui = re.sub(r"[^0-9A-F]","",mac_clean)[:6]
    spinner("Recherche vendeur...", 1.0, LY)
    try:
        r = rget(f"https://api.macvendors.com/{qenc(mac_clean)}", timeout=8)
        section("MAC INFO", LY)
        row("MAC",    mac_clean, LY)
        row("OUI",    oui,       LY)
        if r.status_code == 200: row("Vendeur", r.text.strip(), LY, LG)
        else: row("Vendeur", "Non trouvé", LY, LR)
        lnk("MAClookup.app", f"https://maclookup.app/search/result?mac={qenc(mac_clean)}")
        lnk("Wireshark OUI", "https://www.wireshark.org/tools/oui-lookup.html")
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  15 — HTTP METHOD TESTER
# ══════════════════════════════════════════════

def http_method_tester():
    banner(); section("HTTP METHOD TESTER", LG)
    url = input(LG + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    methods = ["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD","TRACE","CONNECT"]
    section("RÉSULTATS", LG)
    print(LG + f"  {'METHOD':<12} {'STATUS':<10} {'TAILLE':<12} {'SERVER'}")
    print(LG + "  " + "─"*60)
    for method in methods:
        try:
            r = requests.request(method, url, timeout=6, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=False)
            col = LG if r.status_code < 300 else LY if r.status_code < 400 else LR
            server = r.headers.get("Server","?")[:20]
            danger = ""
            if method in ["TRACE","PUT","DELETE"] and r.status_code < 400:
                danger = LR + " [!!!DANGEREUX ACTIVÉ]"
            print(col + f"  {method:<12} {r.status_code:<10} {len(r.content):<12} {server}" + danger)
        except Exception as e: print(DIM+LW + f"  {method:<12} ERR: {str(e)[:40]}")
    pause()

# ══════════════════════════════════════════════
#  16 — CORS CHECKER
# ══════════════════════════════════════════════

def cors_checker():
    banner(); section("CORS MISCONFIGURATION CHECKER", LG)
    url = input(LG + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    origins = ["https://evil.com","null","https://attacker.example.com",url]
    for origin in origins:
        try:
            r = requests.get(url, timeout=6, headers={"Origin":origin,"User-Agent":"Mozilla/5.0"})
            acao = r.headers.get("Access-Control-Allow-Origin","")
            acac = r.headers.get("Access-Control-Allow-Credentials","")
            if acao == "*": print(LR + f"  [VULN] Wildcard CORS — ACAO=*")
            elif acao == origin and origin == "https://evil.com": print(LR + f"  [VULN] Reflète l'origine evil!")
            elif acao and acac.lower()=="true" and acao != url: print(LR + f"  [VULN] Credentials + reflected: {acao}")
            else: print(LG + f"  [OK]  origin={origin[:35]:<40} ACAO={acao[:25] or 'none'}")
        except Exception as e: print(LY + f"  [ERR] {origin}: {e}")
    pause()

# ══════════════════════════════════════════════
#  17 — TOR EXIT NODE CHECK
# ══════════════════════════════════════════════

def tor_check():
    banner(); section("TOR EXIT NODE CHECK", LY)
    ip = input(LY + "  IP à vérifier (vide = ton IP) > ").strip()
    spinner("Vérification TOR...", 1.2, LY)
    try:
        if not ip: ip = requests.get("https://api.ipify.org", timeout=8).text.strip()
        section(f"TOR CHECK — {ip}", LY)
        row("IP", ip, LY)
        r = rget("https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=1.1.1.1", timeout=8)
        exit_ips = set(r.text.strip().split("\n"))
        is_tor = ip in exit_ips
        row("Nœud de sortie TOR", "OUI [!]" if is_tor else "Non", LY, LR if is_tor else LG)
        for name,url in [
            ("TorProject",   "https://check.torproject.org/"),
            ("IPQualityScore",f"https://www.ipqualityscore.com/ip-reputation/proxy-vpn-bot-check/{ip}"),
            ("Shodan",       f"https://www.shodan.io/host/{ip}"),
        ]: lnk(name, url)
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  18 — ROBOTS / SITEMAP
# ══════════════════════════════════════════════

def robots_sitemap():
    banner(); section("ROBOTS / SITEMAP READER", LG)
    domain = input(LG + "  Domaine > ").strip()
    if not domain.startswith("http"): base = f"https://{domain}"
    else: base = domain
    for path in ["/robots.txt","/sitemap.xml","/sitemap_index.xml","/humans.txt"]:
        spinner(f"Récupération {path}...", 0.4, LG)
        try:
            r = requests.get(base+path, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 200:
                section(f"{path}", LG)
                for line in r.text.strip().split("\n")[:60]:
                    print(LG + f"  {line}")
            else: print(LG + f"  {path}  →  HTTP {r.status_code}")
        except Exception as e: print(LG + f"  {path}  →  Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  19 — WAYBACK MACHINE
# ══════════════════════════════════════════════

def wayback():
    banner(); section("WAYBACK MACHINE", LG)
    print(LW + "  1  Dernière snapshot\n  2  Extraire URLs depuis CDX API\n")
    c = input(LG + "  Choix > ").strip()
    if c == "1":
        url = input(LG + "  URL > ").strip()
        spinner("Interrogation archive.org...", 1.0, LG)
        try:
            r = rget(f"http://archive.org/wayback/available?url={url}", timeout=10).json()
            snap = r.get("archived_snapshots",{}).get("closest",{})
            section("SNAPSHOT", LG)
            if snap:
                row("Disponible", snap.get("available","N/A"), LG)
                row("URL",        snap.get("url","N/A"),       LG, LC)
                row("Timestamp",  snap.get("timestamp","N/A"), LG)
            else: print(LG + "  Aucun snapshot trouvé.")
            print(LG + f"\n  Tous les snapshots: https://web.archive.org/web/*/{url}")
        except Exception as e: err(f"Erreur: {e}")
    else:
        domain = input(LG + "  Domaine > ").strip()
        spinner("Requête CDX API...", 1.5, LG)
        try:
            r = rget(f"http://web.archive.org/cdx/search/cdx?url=*.{domain}&output=text&fl=original&collapse=urlkey&limit=100", timeout=15)
            urls = list(set(r.text.strip().split("\n")))
            section(f"URLS TROUVÉES — {len(urls)}", LG)
            for u in sorted(urls)[:80]: print(LG + f"  {u}")
            if len(urls) > 80: print(LG + f"\n  ... et {len(urls)-80} de plus.")
        except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  20 — GOOGLE DORK GENERATOR
# ══════════════════════════════════════════════

def dork_gen():
    banner(); section("GOOGLE DORK GENERATOR", LY)
    target = input(LY + "  Domaine cible > ").strip()
    kw     = input(LY + "  Mot-clé optionnel > ").strip()
    dorks = [
        ("Toutes les pages indexées",  f"site:{target}"),
        ("Sous-domaines",              f"site:*.{target}"),
        ("Pages login/admin",          f"site:{target} inurl:login OR inurl:admin OR inurl:dashboard"),
        ("Fichiers config/env",        f"site:{target} ext:env OR ext:cfg OR ext:ini OR ext:conf"),
        ("Documents",                  f"site:{target} ext:pdf OR ext:doc OR ext:xls OR ext:docx"),
        ("Répertoires ouverts",        f"site:{target} intitle:\"index of\""),
        ("Erreurs SQL",                f"site:{target} intext:\"sql error\" OR intext:\"mysql error\""),
        ("Emails",                     f"site:{target} intext:@{target}"),
        ("WordPress admin",            f"site:{target} inurl:wp-admin"),
        ("phpMyAdmin",                 f"site:{target} inurl:phpmyadmin"),
        ("AWS S3 buckets",             f"site:s3.amazonaws.com \"{target}\""),
        ("GitHub mentions",            f"site:github.com \"{target}\""),
        ("Pastebin",                   f"site:pastebin.com \"{target}\""),
        ("LinkedIn employés",          f"site:linkedin.com inurl:/in/ \"{target}\""),
        ("Fichiers backup",            f"site:{target} ext:bak OR ext:old OR ext:backup OR ext:swp"),
        ("API Keys exposées",          f"site:{target} intext:apikey OR intext:api_key OR intext:secret"),
        ("Cache Google",               f"cache:{target}"),
        ("Logs exposés",               f"site:{target} ext:log"),
        ("Dumps SQL",                  f"site:{target} ext:sql"),
    ]
    if kw: dorks.append((f"Mot-clé: {kw}", f"site:{target} \"{kw}\""))
    section(f"DORKS GÉNÉRÉS — {len(dorks)}", LY)
    for desc,dork in dorks:
        print(LY + f"  {desc:<35}" + LW + f" https://www.google.com/search?q={qenc(dork)}")
    pause()

# ══════════════════════════════════════════════
#  21 — ADVANCED DORK BUILDER
# ══════════════════════════════════════════════

def adv_dork():
    banner(); section("ADVANCED DORK BUILDER", LY)
    print(LY + "  Construis un dork Google personnalisé.\n")
    site    = input(LY + "  site:     > ").strip()
    inurl   = input(LY + "  inurl:    > ").strip()
    intitle = input(LY + "  intitle:  > ").strip()
    intext  = input(LY + "  intext:   > ").strip()
    ext     = input(LY + "  ext:      > ").strip()
    kw      = input(LY + "  keyword   > ").strip()
    parts = []
    if site:    parts.append(f"site:{site}")
    if inurl:   parts.append(f"inurl:{inurl}")
    if intitle: parts.append(f"intitle:{intitle}")
    if intext:  parts.append(f"intext:{intext}")
    if ext:     parts.append(f"ext:{ext}")
    if kw:      parts.append(f'"{kw}"')
    dork = " ".join(parts)
    section("TON DORK", LY)
    print(LY + f"  {dork}")
    print(LW + f"\n  Google: https://www.google.com/search?q={qenc(dork)}")
    print(LW + f"  Bing:   https://www.bing.com/search?q={qenc(dork)}")
    pause()

# ══════════════════════════════════════════════
#  22 — OSINT DORK BUILDER (personne)
# ══════════════════════════════════════════════

def osint_dork_builder():
    banner(); section("OSINT DORK BUILDER — PERSONNE", LY)
    first   = input(LY + "  Prénom      > ").strip()
    last    = input(LY + "  Nom         > ").strip()
    username= input(LY + "  Username    > ").strip()
    email   = input(LY + "  Email       > ").strip()
    phone   = input(LY + "  Téléphone   > ").strip()
    domain  = input(LY + "  Domaine/site> ").strip()
    company = input(LY + "  Entreprise  > ").strip()
    dorks = []
    E = qenc
    names = []
    if first and last: names.append(f"{first} {last}")
    if first: names.append(first)
    if last:  names.append(last)
    for n in names:
        dorks += [
            ("Nom basique",    f'"{n}"'),
            ("LinkedIn",       f'site:linkedin.com "{n}"'),
            ("Twitter/X",      f'site:twitter.com "{n}"'),
            ("GitHub",         f'site:github.com "{n}"'),
            ("CV/Resume",      f'"{n}" (resume OR cv) filetype:pdf'),
        ]
        if company: dorks.append(("Nom + entreprise", f'"{n}" "{company}"'))
    if username:
        dorks += [("Username",  f'"{username}"'), ("Username inurl", f'inurl:{username}')]
    if email:
        dorks += [
            ("Email",         f'"{email}"'),
            ("Email breach",  f'"{email}" (breach OR leak OR dump)'),
            ("Email pastebin",f'site:pastebin.com "{email}"'),
        ]
    if phone:
        clean = re.sub(r"\D","",phone)
        dorks += [("Téléphone", f'"{phone}"'), ("Téléphone digits", f'"{clean}"')]
    if domain:
        dorks += [
            ("Domain all",   f"site:{domain}"),
            ("Domain login", f"site:{domain} inurl:login OR inurl:admin"),
            ("Domain config",f"site:{domain} ext:env OR ext:sql"),
            ("crt.sh",       f"site:crt.sh \"{domain}\""),
        ]
    section(f"DORKS GÉNÉRÉS — {len(dorks)}", LY)
    for desc,dork in [(k,v) for k,v in dorks if v]:
        print(LY + f"  {desc:<30}" + LW + f" https://www.google.com/search?q={E(dork)}")
    pause()

# ══════════════════════════════════════════════
#  23 — PHONE NUMBER INFO
# ══════════════════════════════════════════════

PHONE_DB = {
    "+1":{"country":"USA/Canada","region":"Amérique du Nord","tz":"UTC-5 to UTC-8","fmt":"(XXX) XXX-XXXX"},
    "+7":{"country":"Russie/Kazakhstan","region":"Eurasie","tz":"UTC+2 to +12","fmt":"8 (XXX) XXX-XX-XX"},
    "+33":{"country":"France","region":"Europe","tz":"UTC+1","fmt":"0X XX XX XX XX"},
    "+44":{"country":"Royaume-Uni","region":"Europe","tz":"UTC+0","fmt":"0XXXX XXXXXX"},
    "+49":{"country":"Allemagne","region":"Europe","tz":"UTC+1","fmt":"0XXX XXXXXXXX"},
    "+34":{"country":"Espagne","region":"Europe","tz":"UTC+1","fmt":"XXX XXX XXX"},
    "+39":{"country":"Italie","region":"Europe","tz":"UTC+1","fmt":"XXX XXX XXXX"},
    "+31":{"country":"Pays-Bas","region":"Europe","tz":"UTC+1","fmt":"0XX XXX XXXX"},
    "+32":{"country":"Belgique","region":"Europe","tz":"UTC+1","fmt":"0XXX XX XX XX"},
    "+41":{"country":"Suisse","region":"Europe","tz":"UTC+1","fmt":"0XX XXX XXXX"},
    "+46":{"country":"Suède","region":"Europe","tz":"UTC+1","fmt":"0XX XXX XXXX"},
    "+47":{"country":"Norvège","region":"Europe","tz":"UTC+1","fmt":"XXX XX XXX"},
    "+48":{"country":"Pologne","region":"Europe","tz":"UTC+1","fmt":"XXX XXX XXX"},
    "+212":{"country":"Maroc","region":"Afrique","tz":"UTC+1","fmt":"0XXX XXXXXX"},
    "+213":{"country":"Algérie","region":"Afrique","tz":"UTC+1","fmt":"0XXX XXXXXX"},
    "+216":{"country":"Tunisie","region":"Afrique","tz":"UTC+1","fmt":"XX XXX XXX"},
    "+225":{"country":"Côte d'Ivoire","region":"Afrique","tz":"UTC+0","fmt":"XX XX XX XX XX"},
    "+237":{"country":"Cameroun","region":"Afrique","tz":"UTC+1","fmt":"X XX XX XX XX"},
    "+234":{"country":"Nigeria","region":"Afrique","tz":"UTC+1","fmt":"0XXX XXX XXXX"},
    "+27":{"country":"Afrique du Sud","region":"Afrique","tz":"UTC+2","fmt":"0XX XXX XXXX"},
    "+86":{"country":"Chine","region":"Asie","tz":"UTC+8","fmt":"0XX XXXX XXXX"},
    "+91":{"country":"Inde","region":"Asie","tz":"UTC+5:30","fmt":"XXXXX XXXXX"},
    "+81":{"country":"Japon","region":"Asie","tz":"UTC+9","fmt":"0X XXXX XXXX"},
    "+82":{"country":"Corée du Sud","region":"Asie","tz":"UTC+9","fmt":"0X XXXX XXXX"},
    "+55":{"country":"Brésil","region":"Amérique du Sud","tz":"UTC-3","fmt":"(XX) XXXXX-XXXX"},
    "+52":{"country":"Mexique","region":"Amérique du Nord","tz":"UTC-6","fmt":"XXX XXX XXXX"},
    "+90":{"country":"Turquie","region":"Europe/Asie","tz":"UTC+3","fmt":"0XXX XXX XXXX"},
    "+971":{"country":"Émirats Arabes","region":"Moyen-Orient","tz":"UTC+4","fmt":"0X XXX XXXX"},
}

def phone_info():
    banner(); section("PHONE NUMBER INFO", LM)
    phone = input(LM + "  Numéro (avec indicatif, ex: +33612345678) > ").strip()
    if not phone: pause(); return
    clean = re.sub(r"\s","",phone)
    section("ANALYSE", LM)
    row("Numéro original", phone, LM)
    row("Nettoyé", clean, LM)
    info = None
    for prefix in sorted(PHONE_DB.keys(), key=len, reverse=True):
        if clean.startswith(prefix):
            info = PHONE_DB[prefix]; info["prefix"] = prefix; break
    if info:
        row("Pays",    info.get("country","?"), LM, LG)
        row("Région",  info.get("region","?"),  LM)
        row("Fuseau",  info.get("tz","?"),       LM)
        row("Format",  info.get("fmt","?"),      LM)
        row("Indicatif",info.get("prefix","?"),  LM)
    else:
        warn("Indicatif pays non reconnu.")
    section("RECHERCHE OSINT", LM)
    e = qenc(clean)
    for name,url in [
        ("Google",       f"https://www.google.com/search?q=%22{e}%22"),
        ("NumLookup",    f"https://www.numlookup.com/?number={e}"),
        ("Truecaller",   f"https://www.truecaller.com/search/{e}"),
        ("Sync.me",      f"https://sync.me/search/?number={e}"),
        ("Reverse lookup","https://www.receivesmsonline.net/"),
        ("Pastebin",     f"https://www.google.com/search?q=site:pastebin.com+%22{e}%22"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  24 — EMAIL / MAIL OSINT
# ══════════════════════════════════════════════

def mail_osint():
    banner(); section("EMAIL OSINT", LM)
    email = input(LM + "  Email > ").strip()
    if "@" not in email: err("Email invalide."); pause(); return
    e = qenc(email)
    md5 = hashlib.md5(email.lower().encode()).hexdigest()
    section(f"LIENS OSINT — {email}", LM)
    for name,url in [
        ("HaveIBeenPwned",f"https://haveibeenpwned.com/account/{e}"),
        ("Google",        f"https://www.google.com/search?q=%22{e}%22"),
        ("GitHub code",   f"https://github.com/search?q={e}&type=code"),
        ("Gravatar",      f"https://www.gravatar.com/avatar/{md5}"),
        ("EmailRep.io",   f"https://emailrep.io/{e}"),
        ("XposedOrNot",   f"https://xposedornot.com/search/{e}"),
        ("Hunter.io",     f"https://hunter.io/email-verifier/{e}"),
        ("Pastebin dork", f"https://www.google.com/search?q=site:pastebin.com+%22{e}%22"),
    ]: lnk(name, url)
    spinner("Vérification XposedOrNot...", 1.0, LM)
    try:
        r = rget(f"https://api.xposedornot.com/v1/check-email/{qenc(email)}", timeout=10)
        section("XPOSEDORNOT RÉSULTAT", LM)
        if r.status_code == 200:
            data = r.json(); breaches = data.get("breaches",[])
            flat = [b[0] if isinstance(b,list) else str(b) for b in breaches]
            if flat:
                print(LR + f"  [!!!] Trouvé dans {len(flat)} breach(es):")
                for b in flat: print(LR + f"    [!] {b}")
            else: print(LG + "  [OK] Aucune breach trouvée.")
        elif r.status_code == 404: print(LG + "  [OK] Email propre.")
        elif r.status_code == 429: warn("Rate limit atteint (100/jour).")
    except Exception as e: warn(f"XposedOrNot indisponible: {e}")
    pause()

# ══════════════════════════════════════════════
#  25 — USERNAME TRACKER
# ══════════════════════════════════════════════

SITES = [
    ("GitHub",       "https://github.com/{}"),
    ("GitLab",       "https://gitlab.com/{}"),
    ("Twitter/X",    "https://twitter.com/{}"),
    ("Instagram",    "https://www.instagram.com/{}"),
    ("TikTok",       "https://www.tiktok.com/@{}"),
    ("YouTube",      "https://www.youtube.com/@{}"),
    ("Reddit",       "https://www.reddit.com/user/{}"),
    ("Twitch",       "https://www.twitch.tv/{}"),
    ("Pinterest",    "https://www.pinterest.com/{}"),
    ("Tumblr",       "https://www.tumblr.com/{}"),
    ("LinkedIn",     "https://www.linkedin.com/in/{}"),
    ("SoundCloud",   "https://soundcloud.com/{}"),
    ("Spotify",      "https://open.spotify.com/user/{}"),
    ("Flickr",       "https://www.flickr.com/people/{}"),
    ("DeviantArt",   "https://www.deviantart.com/{}"),
    ("Medium",       "https://medium.com/@{}"),
    ("Keybase",      "https://keybase.io/{}"),
    ("HackerNews",   "https://news.ycombinator.com/user?id={}"),
    ("ProductHunt",  "https://www.producthunt.com/@{}"),
    ("Steam",        "https://steamcommunity.com/id/{}"),
    ("Pastebin",     "https://pastebin.com/u/{}"),
    ("Codecademy",   "https://www.codecademy.com/profiles/{}"),
    ("Dev.to",       "https://dev.to/{}"),
    ("HackTheBox",   "https://app.hackthebox.com/users/{}"),
    ("TryHackMe",    "https://tryhackme.com/p/{}"),
    ("Replit",       "https://replit.com/@{}"),
    ("Npm",          "https://www.npmjs.com/~{}"),
    ("PyPI",         "https://pypi.org/user/{}"),
    ("Behance",      "https://www.behance.net/{}"),
    ("Dribbble",     "https://dribbble.com/{}"),
    ("VK",           "https://vk.com/{}"),
    ("Telegram",     "https://t.me/{}"),
    ("Mastodon",     "https://mastodon.social/@{}"),
    ("Discord app",  "https://discord.com/users/{}"),
    ("Snapchat",     "https://www.snapchat.com/add/{}"),
    ("Bluesky",      "https://bsky.app/profile/{}"),
    ("GitHubGist",   "https://gist.github.com/{}"),
    ("HackerEarth",  "https://www.hackerearth.com/@{}"),
    ("Codeforces",   "https://codeforces.com/profile/{}"),
    ("LeetCode",     "https://leetcode.com/{}"),
    ("AtCoder",      "https://atcoder.jp/users/{}"),
    ("Duolingo",     "https://www.duolingo.com/profile/{}"),
    ("Genius",       "https://genius.com/{}"),
    ("Mixcloud",     "https://www.mixcloud.com/{}"),
    ("Bandcamp",     "https://www.bandcamp.com/{}"),
    ("Wattpad",      "https://www.wattpad.com/user/{}"),
    ("Archive.org",  "https://archive.org/search.php?query={}"),
    ("Gravatar",     "https://www.gravatar.com/{}"),
    ("CafeBazaar",   "https://cafebazaar.ir/developer/{}"),
    ("Crunchbase",   "https://www.crunchbase.com/person/{}"),
    ("AngelList",    "https://angel.co/u/{}"),
    ("Fiverr",       "https://www.fiverr.com/{}"),
    ("Upwork",       "https://www.upwork.com/freelancers/{}"),
    ("About.me",     "https://about.me/{}"),
    ("Linktree",     "https://linktr.ee/{}"),
    ("Strava",       "https://www.strava.com/athletes/{}"),
    ("Vimeo",        "https://vimeo.com/{}"),
    ("Imgur",        "https://imgur.com/user/{}"),
    ("OK.ru",        "https://ok.ru/{}"),
    ("Roblox",       "https://www.roblox.com/user.aspx?username={}"),
]

def username_tracker():
    banner(); section("USERNAME TRACKER — 60+ SITES", LM)
    username = input(LM + "  Username > ").strip()
    if not username: pause(); return
    print(LM + "  1  Scan rapide (génère les liens)\n  2  Scan actif (vérifie HTTP 200)\n")
    c = input(LM + "  Choix > ").strip()

    if c == "2":
        bar("  Scan en cours", 40, 0.015, LM, M)
        found = []
        def chk(site_url):
            site, url_tpl = site_url
            url = url_tpl.format(username)
            try:
                r = requests.get(url, timeout=5, headers=REQ_HDR, allow_redirects=True)
                if r.status_code == 200 and len(r.content) > 200:
                    return (site, url, True)
            except: pass
            return (site, url, False)
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
            results = list(ex.map(chk, SITES))
        section("PROFILS TROUVÉS", LM)
        for site,url,found_flag in results:
            if found_flag:
                print(LG + f"  [+]  {site:<20}" + LW + f" {url}")
                found.append(site)
        print(LM + f"\n  {len(found)} profil(s) actif(s) trouvé(s).")
    else:
        section("LIENS GÉNÉRÉS — 60+ SITES", LM)
        for site, url_tpl in SITES:
            print(LM + f"  {site:<20}" + LW + f" {url_tpl.format(username)}")
    pause()

# ══════════════════════════════════════════════
#  26 — BREACH SEARCH ENGINE
# ══════════════════════════════════════════════

def breach_engine():
    banner(); section("BREACH SEARCH ENGINE", LR)
    print(LR + "  1  ZSearcher.fr\n  2  OathNet.org\n  3  HaveIBeenPwned\n"
               "  4  Tous les liens breach\n  5  Check password HIBP\n"
               "  6  XposedOrNot API [GRATUIT, sans clé]\n"
               "  7  Domaine breach search\n")
    c = input(LC + "  Choix > ").strip()

    if c == "1":
        q = input(LC + "  Recherche > ").strip(); e = qenc(q)
        section("ZSEARCHER.FR", LR)
        for name,url in [
            ("ZSearcher main",   "https://zsearcher.fr/"),
            ("ZSearcher search", f"https://zsearcher.fr/search?q={e}"),
        ]: lnk(name, url)
    elif c == "2":
        q = input(LC + "  Recherche > ").strip(); e = qenc(q)
        section("OATHNET.ORG", LR)
        lnk("OathNet search", f"https://oathnet.org/search?q={e}")
    elif c == "3":
        email = input(LC + "  Email > ").strip(); e = qenc(email)
        section("HAVEIBEENPWNED", LR)
        lnk("Check email", f"https://haveibeenpwned.com/account/{e}")
        try:
            r = rget(f"https://haveibeenpwned.com/api/v3/breachedaccount/{e}",
                     timeout=8)
            if r.status_code == 200:
                breaches = r.json()
                print(LR + f"\n  [!!!] Trouvé dans {len(breaches)} breach(es)!")
                for b in breaches[:10]: print(LR + f"    [!] {b.get('Name','?')}")
            elif r.status_code == 404: print(LG + "\n  [OK] Email propre!")
            else: print(LY + f"  HTTP {r.status_code} (API key peut-être requise)")
        except Exception as e: warn(f"HIBP: {e}")
    elif c == "4":
        q = input(LC + "  Recherche > ").strip(); e = qenc(q)
        section("BREACH LINKS", LR)
        for name,url in [
            ("ZSearcher.fr",  f"https://zsearcher.fr/search?q={e}"),
            ("OathNet.org",   f"https://oathnet.org/search?q={e}"),
            ("HaveIBeenPwned",f"https://haveibeenpwned.com/account/{e}"),
            ("DeHashed",      f"https://dehashed.com/search?query={e}"),
            ("IntelX",        f"https://intelx.io/?s={e}"),
            ("LeakIX",        f"https://leakix.net/search?scope=leaks&q={e}"),
            ("Breachbase",    f"https://www.breachbase.pw/search/?search={e}"),
        ]: lnk(name, url)
    elif c == "5":
        pwd = input(LC + "  Mot de passe > ").strip()
        if not pwd: pause(); return
        sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        spinner("Vérification HIBP PwnedPasswords...", 1.0, LR)
        try:
            r = rget(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=8)
            found = False
            for line in r.text.splitlines():
                h, count = line.split(":")
                if h == suffix:
                    print(LR + f"\n  [!!!] Trouvé {count} fois dans des leaks! Change-le!")
                    found = True; break
            if not found: print(LG + "\n  [OK] Non trouvé dans HIBP.")
            print(DIM + "\n  Seuls 5 chars du SHA1 sont envoyés — MDP jamais transmis.")
        except Exception as e: err(f"Erreur: {e}")
    elif c == "6":
        xposedornot()
        return
    elif c == "7":
        domain = input(LC + "  Domaine > ").strip(); e = qenc(domain)
        section(f"DOMAIN BREACH — {domain}", LR)
        for name,url in [
            ("HaveIBeenPwned domain",f"https://haveibeenpwned.com/DomainSearch"),
            ("DeHashed",             f"https://dehashed.com/search?query={e}"),
            ("BreachDirectory",      f"https://breachdirectory.com/"),
            ("LeakIX",               f"https://leakix.net/search?scope=leaks&q={e}"),
        ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  27 — XPOSEDORNOT API (gratuit, sans clé)
# ══════════════════════════════════════════════

def xposedornot():
    banner(); section("XPOSEDORNOT API", LR)
    XON = "https://api.xposedornot.com/v1"
    print(LR + "  Gratuit — Sans clé — Résultats directs\n")
    print(LR + "  1  Check email (breaches)\n  2  Analytics détaillées\n"
               "  3  Check pastes\n  4  Scan complet\n  5  Check password HIBP\n")
    c = input(LC + "  Choix > ").strip()

    if c in ["1","2","3","4"]:
        email = input(LC + "  Email > ").strip()
        if "@" not in email: err("Email invalide."); pause(); return

    if c == "1":
        spinner(f"XposedOrNot check...", 1.2, LR)
        try:
            r = rget(f"{XON}/check-email/{qenc(email)}", timeout=10)
            if r.status_code == 200:
                data = r.json(); breaches = data.get("breaches",[])
                flat = [b[0] if isinstance(b,list) else str(b) for b in breaches]
                if flat:
                    section(f"BREACH(ES) — {len(flat)}", LR)
                    for b in flat: print(LR + f"  [!]  {b}")
                else: print(LG + "  [OK] Aucune breach.")
            elif r.status_code == 404: print(LG + "  [OK] Email propre.")
            elif r.status_code == 429: warn("Rate limit (100/jour).")
        except Exception as e: err(f"Erreur: {e}")

    elif c == "2":
        spinner("Récupération analytics...", 1.5, LR)
        try:
            r = rget(f"{XON}/breach-analytics?email={qenc(email)}", timeout=12)
            if r.status_code == 200:
                data = r.json()
                metrics = data.get("metrics",{})
                xposed  = data.get("xposed_data",{})
                if metrics:
                    section("STATISTIQUES", LR)
                    for k,v in metrics.items(): row(k.replace("_"," ").title(), v, LR)
                if xposed:
                    section("DONNÉES EXPOSÉES", LR)
                    for cat,items in xposed.items():
                        if items:
                            val = ", ".join(items) if isinstance(items,list) else str(items)
                            row(cat.replace("_"," ").title(), val[:70], LR)
        except Exception as e: err(f"Erreur: {e}")

    elif c == "3":
        spinner("Recherche pastes...", 1.0, LR)
        try:
            r = rget(f"{XON}/pastes?email={qenc(email)}", timeout=10)
            if r.status_code == 200:
                pastes = r.json().get("pastes",[])
                section(f"PASTES — {len(pastes)}", LR)
                for p in pastes:
                    if isinstance(p, dict): print(LR + f"  [!]  {p.get('source','?')}  {p.get('id','?')}")
                    else: print(LR + f"  [!]  {p}")
            elif r.status_code == 404: print(LG + "  [OK] Aucun paste.")
        except Exception as e: err(f"Erreur: {e}")

    elif c == "4":
        spinner("Scan complet XposedOrNot...", 2.0, LR)
        for endpoint in [f"{XON}/check-email/{qenc(email)}", f"{XON}/pastes?email={qenc(email)}"]:
            try:
                r = rget(endpoint, timeout=10)
                if "check-email" in endpoint:
                    if r.status_code == 200:
                        flat = [b[0] if isinstance(b,list) else str(b) for b in r.json().get("breaches",[])]
                        print(LR + f"  Breaches: {len(flat)}")
                        for b in flat: print(LR + f"    [!] {b}")
                    else: print(LG + f"  Breaches: 0")
                else:
                    time.sleep(0.6)
                    if r.status_code == 200:
                        pastes = r.json().get("pastes",[])
                        print(LR + f"  Pastes: {len(pastes)}")
            except Exception as e: err(f"Erreur: {e}")

    elif c == "5":
        pwd = input(LC + "  Mot de passe > ").strip()
        sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        try:
            r = rget(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=8)
            found = False
            for line in r.text.splitlines():
                h, count = line.split(":")
                if h == suffix:
                    print(LR + f"\n  [!!!] Trouvé {count} fois! Changeez ce mot de passe!")
                    found = True; break
            if not found: print(LG + "\n  [OK] Non trouvé dans HIBP.")
        except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  28 — PROFILE BUILDER
# ══════════════════════════════════════════════

def profile_builder():
    banner(); section("PROFILE BUILDER — OSINT", LM)
    name     = input(LM + "  Nom complet > ").strip()
    username = input(LM + "  Username    > ").strip()
    email    = input(LM + "  Email       > ").strip()
    location = input(LM + "  Localisation> ").strip()
    section("RÉSUMÉ PROFIL", LM)
    if name:     row("Nom",          name,     LM)
    if username: row("Username",     username, LM)
    if location: row("Localisation", location, LM)
    if email:
        row("Email",   email, LM)
        md5 = hashlib.md5(email.lower().encode()).hexdigest()
        row("Gravatar", f"https://gravatar.com/avatar/{md5}", LM, LC)
    enc = qenc(name)
    if name:
        section("LIENS RECHERCHE NOM", LM)
        for nm,url in [
            ("Google",     f"https://www.google.com/search?q=%22{enc}%22"),
            ("LinkedIn",   f"https://www.linkedin.com/search/results/people/?keywords={enc}"),
            ("Twitter",    f"https://twitter.com/search?q=%22{enc}%22"),
            ("Facebook",   f"https://www.facebook.com/search/top/?q={enc}"),
            ("ZSearcher",  f"https://zsearcher.fr/search?q={enc}"),
        ]: lnk(nm, url, LM)
    if username:
        section("PROFILS PRINCIPAUX", LM)
        for site,tpl in SITES[:15]:
            print(LM + f"  {site:<20}" + LW + f" {tpl.format(username)}")
    pause()

# ══════════════════════════════════════════════
#  29 — HASH TOOLS
# ══════════════════════════════════════════════

def hash_tools():
    banner(); section("HASH TOOLS", LM)
    print(LM + "  1  Générer hashes depuis du texte\n  2  Hash cracker (wordlist)\n  3  Liens lookup hash\n")
    c = input(LM + "  Choix > ").strip()

    if c == "1":
        text = input(LM + "  Texte > ").strip()
        if not text: pause(); return
        section("HASHES GÉNÉRÉS", LM)
        for name,fn in [("MD5",hashlib.md5),("SHA1",hashlib.sha1),("SHA224",hashlib.sha224),
                        ("SHA256",hashlib.sha256),("SHA384",hashlib.sha384),("SHA512",hashlib.sha512),
                        ("SHA3-256",hashlib.sha3_256),("SHA3-512",hashlib.sha3_512)]:
            row(name, fn(text.encode()).hexdigest(), LM)
        row("Base64", base64.b64encode(text.encode()).decode(), LM)
        row("Hex",    text.encode().hex(), LM)

    elif c == "2":
        target = input(LM + "  Hash cible > ").strip().lower()
        wl_path = input(LM + "  Wordlist (vide = rockyou ou liste intégrée) > ").strip()

        length_map = {
            32:  ("MD5",    hashlib.md5),
            40:  ("SHA1",   hashlib.sha1),
            64:  ("SHA256", hashlib.sha256),
            128: ("SHA512", hashlib.sha512),
            56:  ("SHA224", hashlib.sha224),
        }
        detected = length_map.get(len(target))
        if not detected:
            err("Type de hash non détectable depuis la longueur."); pause(); return
        algo_name, fn = detected
        print(LY + f"\n  Détecté: {algo_name}")

        # Essai wordlist fichier
        paths_to_try = []
        if wl_path: paths_to_try.append(wl_path)
        # Chemins communs Termux/Linux
        paths_to_try += [
            "/sdcard/rockyou.txt",
            "/data/data/com.termux/files/home/rockyou.txt",
            "/usr/share/wordlists/rockyou.txt",
            os.path.expanduser("~/rockyou.txt"),
        ]

        wordlist_file = next((p for p in paths_to_try if os.path.isfile(p)), None)

        if wordlist_file:
            print(LY + f"  Wordlist: {wordlist_file}\n")
            start = time.time()
            try:
                with open(wordlist_file,"r",encoding="utf-8",errors="ignore") as f:
                    for i, line in enumerate(f):
                        word = line.strip()
                        if fn(word.encode()).hexdigest() == target:
                            elapsed = time.time() - start
                            ok(f"CRACKÉ → {word}  ({i+1} mots en {elapsed:.2f}s)")
                            pause(); return
                        if i % 100000 == 0 and i > 0:
                            print(LY + f"\r  {i:,} mots essayés...", end="", flush=True)
                err("Non trouvé dans la wordlist.")
            except Exception as e: err(f"Erreur: {e}")
        else:
            # Wordlist intégrée légère
            common = ["password","123456","password1","qwerty","abc123","admin","letmein",
                      "monkey","password123","1234567890","sunshine","princess","football",
                      "welcome","shadow","master","dragon","654321","pass","iloveyou",
                      "hello","charlie","donald","password2","qwerty123","111111","test"]
            print(LY + f"  Aucune wordlist trouvée — test {len(common)} mots communs...\n")
            for word in common:
                if fn(word.encode()).hexdigest() == target:
                    ok(f"CRACKÉ → {word}")
                    pause(); return
            warn("Non trouvé. Place rockyou.txt dans ~/rockyou.txt pour un scan complet.")

    elif c == "3":
        h = input(LM + "  Hash > ").strip()
        section("LIENS LOOKUP", LM)
        for name,url in [
            ("CrackStation",   "https://crackstation.net/"),
            ("Hashes.com",     f"https://hashes.com/en/decrypt/hash#{h}"),
            ("MD5Decrypt",     f"https://md5decrypt.net/en/#answer={h}"),
            ("HashKiller",     "https://hashkiller.io/listmanager"),
            ("OnlineHashCrack","https://www.onlinehashcrack.com/"),
        ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  30 — PASSWORD TOOLS
# ══════════════════════════════════════════════

def password_tools():
    banner(); section("PASSWORD TOOLS", LM)
    print(LM + "  1  Générer mot de passe sécurisé\n  2  Tester la force\n  3  Générer en masse\n  4  Passphrase\n")
    c = input(LM + "  Choix > ").strip()

    if c == "1":
        try: length = int(input(LM + "  Longueur (défaut 20) > ").strip() or "20")
        except: length = 20
        use_u = input(LM + "  Majuscules? [Y/n] > ").lower() != "n"
        use_d = input(LM + "  Chiffres? [Y/n] > ").lower() != "n"
        use_s = input(LM + "  Symboles? [Y/n] > ").lower() != "n"
        pool = string.ascii_lowercase
        if use_u: pool += string.ascii_uppercase
        if use_d: pool += string.digits
        if use_s: pool += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        if not pool: pool = string.ascii_letters + string.digits
        section("MOTS DE PASSE GÉNÉRÉS", LM)
        for i in range(5):
            pwd = "".join(secrets.choice(pool) for _ in range(length))
            rainbow(f"  [{i+1}]  {pwd}")

    elif c == "2":
        pwd = input(LM + "  Mot de passe > ").strip()
        section("ANALYSE DE FORCE", LM)
        checks = [
            (len(pwd)>=8,  "Longueur >= 8"),
            (len(pwd)>=12, "Longueur >= 12"),
            (len(pwd)>=16, "Longueur >= 16"),
            (any(ch.isupper() for ch in pwd), "Majuscules"),
            (any(ch.islower() for ch in pwd), "Minuscules"),
            (any(ch.isdigit() for ch in pwd), "Chiffres"),
            (any(ch in "!@#$%^&*()-_=+[]{}|;:,.<>?" for ch in pwd), "Caractères spéciaux"),
        ]
        score = sum(1 for passed,_ in checks if passed)
        for passed, label in checks:
            print((LG+"  [OK] " if passed else LR+"  [!!] ")+LW+label)
        ratings = {7:"Très Fort",6:"Fort",5:"Bon",4:"Moyen",3:"Faible",2:"Très Faible",1:"Terrible",0:"Nul"}
        print(LM + f"\n  Score: {score}/7  —  " + ratings.get(score,"?"))
        # HIBP check
        sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix,suffix = sha1[:5],sha1[5:]
        try:
            r = rget(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=8)
            for line in r.text.splitlines():
                h, count = line.split(":")
                if h == suffix:
                    print(LR + f"\n  [!!!] Mot de passe compromis — Vu {count} fois dans des leaks!"); break
            else: print(LG + "\n  [OK] Non compromis selon HIBP.")
        except: warn("HIBP indisponible.")

    elif c == "3":
        try:
            n = int(input(LM + "  Combien? > ").strip() or "10")
            l = int(input(LM + "  Longueur? > ").strip() or "20")
        except: n, l = 10, 20
        pool = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
        section(f"{n} MOTS DE PASSE", LM)
        for i in range(n):
            pwd = "".join(secrets.choice(pool) for _ in range(l))
            rainbow(f"  {i+1:>3}.  {pwd}")

    elif c == "4":
        words = ["correct","horse","battery","staple","ocean","cloud","fire","storm",
                 "alpha","beta","gamma","delta","echo","foxtrot","tango","victor",
                 "river","mountain","forest","shadow","light","dark","red","blue"]
        try: n = int(input(LM + "  Nombre de mots (défaut 4) > ").strip() or "4")
        except: n = 4
        section("PASSPHRASES GÉNÉRÉES", LM)
        for i in range(5):
            phrase = "-".join(secrets.choice(words) for _ in range(n))
            rainbow(f"  [{i+1}]  {phrase}")
    pause()

# ══════════════════════════════════════════════
#  31 — METADATA EXTRACTOR (images)
# ══════════════════════════════════════════════

def metadata_extractor():
    banner(); section("METADATA EXTRACTOR (EXIF)", LG)
    if not PIL_OK:
        err("Pillow non installé.")
        warn("Installe avec: pip install Pillow"); pause(); return
    path = input(LG + "  Chemin image > ").strip().strip('"').strip("'")
    if not path: pause(); return
    # Termux: support /sdcard/
    if path.startswith("~/"):
        path = os.path.expanduser(path)
    spinner("Lecture EXIF...", 0.6, LG)
    try:
        img = Image.open(path)
        section("INFOS IMAGE", LG)
        row("Format", img.format, LG); row("Mode", img.mode, LG)
        row("Taille", f"{img.size[0]} x {img.size[1]} px", LG)
        try:
            exif_data = img.getexif()
            gps_data = {}
            if exif_data:
                section("DONNÉES EXIF", LG)
                for tid, val in exif_data.items():
                    tag_name = TAGS.get(tid, str(tid))
                    if isinstance(val, bytes): val = val.hex()
                    if tag_name == "GPSInfo" and isinstance(val, dict):
                        for k,v in val.items():
                            gps_data[GPSTAGS.get(k,k)] = v
                    else:
                        row(str(tag_name), str(val)[:80], LG)
            if gps_data:
                section("DONNÉES GPS", LG)
                for k,v in gps_data.items(): row(str(k), str(v), LG)
                try:
                    def _dms(dms, ref):
                        d,m,s = float(dms[0]),float(dms[1]),float(dms[2])
                        decimal = d + m/60 + s/3600
                        if ref in ["S","W"]: decimal = -decimal
                        return decimal
                    lat = _dms(gps_data["GPSLatitude"],  gps_data["GPSLatitudeRef"])
                    lon = _dms(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
                    print(LG + f"\n  Coordonnées: {lat:.6f}, {lon:.6f}")
                    lnk("Google Maps", f"https://www.google.com/maps?q={lat},{lon}")
                except: pass
            else: print(LG + "  Aucun EXIF trouvé dans cette image.")
        except Exception as ex: warn(f"Erreur EXIF: {ex}")
    except FileNotFoundError: err("Fichier non trouvé.")
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  32 — SOCIAL / PASTE / DARK WEB
# ══════════════════════════════════════════════

def social_search():
    banner(); section("SOCIAL MEDIA SEARCH", LM)
    q = input(LM + "  Nom / username / hashtag > ").strip(); e = qenc(q)
    for name,url in [
        ("Twitter/X",    f"https://twitter.com/search?q={e}&f=live"),
        ("Instagram",    f"https://www.instagram.com/explore/tags/{e}/"),
        ("TikTok",       f"https://www.tiktok.com/search?q={e}"),
        ("Facebook",     f"https://www.facebook.com/search/top/?q={e}"),
        ("LinkedIn",     f"https://www.linkedin.com/search/results/people/?keywords={e}"),
        ("Reddit",       f"https://www.reddit.com/search/?q={e}"),
        ("YouTube",      f"https://www.youtube.com/results?search_query={e}"),
        ("Telegram",     f"https://t.me/s/{q}"),
        ("Bluesky",      f"https://bsky.app/search?q={e}"),
        ("Mastodon",     f"https://mastodon.social/search?q={e}"),
    ]: lnk(name, url)
    pause()

def paste_search():
    banner(); section("PASTE SEARCH", LM)
    q = input(LM + "  Terme de recherche > ").strip(); e = qenc(q)
    for name,url in [
        ("Google Pastebin", f"https://www.google.com/search?q=site:pastebin.com+%22{e}%22"),
        ("Google Gist",     f"https://www.google.com/search?q=site:gist.github.com+%22{e}%22"),
        ("Psbdmp",          f"https://psbdmp.ws/api/search/{e}"),
        ("Grep.app",        f"https://grep.app/search?q={e}"),
        ("GitHub code",     f"https://github.com/search?q={e}&type=code"),
        ("Pastebin.com",    f"https://pastebin.com/search?q={e}"),
    ]: lnk(name, url)
    pause()

def darkweb_search():
    banner(); section("DARK WEB SEARCH", LR)
    print(LR + "  Moteurs clearnet indexant du contenu .onion\n")
    q = input(LC + "  Terme > ").strip(); e = qenc(q)
    for name,url in [
        ("Ahmia",       f"https://ahmia.fi/search/?q={e}"),
        ("DarkSearch",  f"https://darksearch.io/search?query={e}"),
        ("DeHashed",    f"https://dehashed.com/search?query={e}"),
        ("IntelX",      f"https://intelx.io/?s={e}"),
        ("Torch",       "https://torch.webhosting.rip/"),
    ]: lnk(name, url)
    pause()

def vuln_search():
    banner(); section("CVE / VULNERABILITY SEARCH", LR)
    q = input(LR + "  Logiciel / CVE ID > ").strip(); e = qenc(q)
    for name,url in [
        ("NVD NIST",      f"https://nvd.nist.gov/vuln/search/results?query={e}"),
        ("CVE Details",   f"https://www.cvedetails.com/google-search-results.php?q={e}"),
        ("Exploit-DB",    f"https://www.exploit-db.com/search?q={e}"),
        ("Shodan CVE",    f"https://www.shodan.io/search?query=vuln:{q}"),
        ("PacketStorm",   f"https://packetstormsecurity.com/search/?q={e}"),
        ("GitHub Advisories",f"https://github.com/advisories?query={e}"),
        ("Snyk DB",       f"https://security.snyk.io/vuln?search={e}"),
        ("MITRE ATT&CK",  "https://attack.mitre.org/"),
    ]: lnk(name, url)
    pause()

def reverse_image():
    banner(); section("REVERSE IMAGE SEARCH", LM)
    url = input(LM + "  URL image > ").strip()
    if not url: pause(); return
    e = qenc(url)
    for name,u in [
        ("Google Images",  f"https://www.google.com/searchbyimage?image_url={e}"),
        ("Yandex Images",  f"https://yandex.com/images/search?url={e}&rpt=imageview"),
        ("TinEye",         f"https://tineye.com/search?url={e}"),
        ("SauceNAO",       f"https://saucenao.com/search.php?url={e}"),
        ("Bing Visual",    f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{e}"),
    ]: lnk(name, u)
    pause()

def osint_framework():
    banner(); section("OSINT FRAMEWORK & RESSOURCES", LM)
    for name,url in [
        ("OSINT Framework",   "https://osintframework.com"),
        ("IntelTechniques",   "https://inteltechniques.com/tools/index.html"),
        ("ZSearcher.fr",      "https://zsearcher.fr/"),
        ("Shodan",            "https://www.shodan.io"),
        ("Censys",            "https://search.censys.io"),
        ("HaveIBeenPwned",    "https://haveibeenpwned.com"),
        ("URLScan.io",        "https://urlscan.io"),
        ("VirusTotal",        "https://www.virustotal.com"),
        ("Wayback Machine",   "https://web.archive.org"),
        ("BGPView",           "https://bgpview.io"),
        ("Grep.app",          "https://grep.app"),
        ("DeHashed",          "https://dehashed.com"),
        ("IntelX",            "https://intelx.io"),
        ("LeakIX",            "https://leakix.net"),
        ("Hunter.io",         "https://hunter.io"),
        ("crt.sh",            "https://crt.sh"),
        ("SecurityTrails",    "https://securitytrails.com"),
        ("GrayHatWarfare S3", "https://grayhatwarfare.com"),
        ("OTX AlienVault",    "https://otx.alienvault.com"),
        ("FOFA",              "https://fofa.info"),
        ("ZoomEye",           "https://www.zoomeye.org"),
        ("Awesome OSINT",     "https://github.com/jivoi/awesome-osint"),
    ]: lnk(name, url)
    pause()

def archive_links():
    banner(); section("ARCHIVE LINKS", LG)
    url = input(LG + "  URL > ").strip()
    if not url.startswith("http"): url = "https://" + url
    for name,u in [
        ("Wayback Machine", f"https://web.archive.org/web/*/{url}"),
        ("Archive.ph",      f"https://archive.ph/{url}"),
        ("CachedView",      f"https://cachedview.nl/"),
        ("Google Cache",    f"https://webcache.googleusercontent.com/search?q=cache:{url}"),
    ]: lnk(name, u)
    pause()

def file_osint():
    banner(); section("FILE OSINT", LY)
    domain = input(LY + "  Domaine > ").strip()
    section("LIENS FICHIERS SENSIBLES", LY)
    for label,ext in [
        ("PDF","pdf"),("Word","doc OR docx"),("Excel","xls OR xlsx"),
        ("CSV","csv"),("SQL","sql"),("ENV","env"),("LOG","log"),
        ("BAK","bak"),("ZIP","zip"),("XML","xml"),("CONFIG","conf OR config"),
        ("JSON","json"),("YAML","yaml OR yml"),("Key files","key OR pem"),
    ]:
        q = qenc(f"site:{domain} ext:{ext}")
        print(LY + f"  {label:<14}" + LW + f" https://www.google.com/search?q={q}")
    pause()

def public_cameras():
    banner(); section("PUBLIC CAMERA FEEDS", LR)
    print(LR + "  Recherches pour flux caméras indexés publiquement.\n")
    location = input(LC + "  Localisation (ville/pays, vide = global) > ").strip()
    queries = [
        ("Webcams génériques",  "has_screenshot:true port:80"),
        ("Hikvision",          "server:Hikvision-Webs"),
        ("RTSP streams",        "port:554 has_screenshot:true"),
        ("Webcam netcam",       "title:netcam"),
        ("Axis camera",         "server:AXIS"),
    ]
    section("SHODAN CAMERAS", LR)
    for name,q in queries:
        fq = q + (f" city:{location}" if location else "")
        print(LR + f"  {name:<28}" + LW + f" https://www.shodan.io/search?query={qenc(fq)}")
    section("RÉPERTOIRES PUBLICS", LR)
    for name,url in [
        ("Insecam",  "http://www.insecam.org/"),
        ("EarthCam", "https://www.earthcam.com/"),
        ("Windy",    "https://www.windy.com/"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  33 — QUICK RECON (tout-en-un)
# ══════════════════════════════════════════════

def quick_recon():
    banner(); section("QUICK RECON — TOUT-EN-UN", LG)
    domain = input(LG + "  Domaine > ").strip()
    if not domain: pause(); return
    bar("  Recon en cours", 40, 0.025, LG, G)
    section("DNS", LG)
    try:
        ip = socket.gethostbyname(domain); row("A Record", ip, LG)
        try: row("Reverse DNS", socket.gethostbyaddr(ip)[0], LG)
        except: pass
    except Exception as e: row("DNS", f"Échec: {e}", LG, LR)
    section("GÉO IP", LG)
    try:
        d = rget(f"https://ipapi.co/{socket.gethostbyname(domain)}/json", timeout=8).json()
        for f in ["country_name","city","org","asn","timezone"]:
            row(f, d.get(f,"N/A"), LG)
    except: pass
    section("HTTP", LG)
    try:
        r = requests.get(f"https://{domain}", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        row("Status", str(r.status_code), LG)
        row("Server", r.headers.get("Server","N/A"), LG)
        row("CSP", "Présent" if r.headers.get("Content-Security-Policy") else "MANQUANT", LG,
            LG if r.headers.get("Content-Security-Policy") else LR)
        row("HSTS", "Présent" if r.headers.get("Strict-Transport-Security") else "MANQUANT", LG,
            LG if r.headers.get("Strict-Transport-Security") else LY)
    except: pass
    section("SOUS-DOMAINES RAPIDES", LG)
    for sub in ["www","mail","api","admin","dev","staging","ftp","vpn","cdn","blog","shop","app"]:
        t = f"{sub}.{domain}"
        try: ip2=socket.gethostbyname(t); print(LG+f"  [+]  {t:<42}"+LW+f" → {ip2}")
        except: pass
    section("LIENS UTILES", LG)
    e = qenc(domain)
    for name,url in [
        ("Shodan",    f"https://www.shodan.io/search?query={e}"),
        ("VirusTotal",f"https://www.virustotal.com/gui/domain/{domain}"),
        ("URLScan",   f"https://urlscan.io/search/#{e}"),
        ("Wayback",   f"https://web.archive.org/web/*/{domain}"),
        ("crt.sh",    f"https://crt.sh/?q=%.{domain}"),
        ("SecurityTrails",f"https://securitytrails.com/domain/{domain}/dns"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  34 — NETWORK INFO
# ══════════════════════════════════════════════

def network_info():
    banner(); section("INFORMATIONS RÉSEAU LOCAL", LG)
    spinner("Collecte d'infos...", 0.8, LG)
    hn = socket.gethostname()
    try: lip = socket.gethostbyname(hn)
    except: lip = "N/A"
    row("Hostname",   hn,  LG)
    row("IP locale",  lip, LG)
    row("Plateforme", platform.system()+" "+platform.release(), LG)
    row("Python",     sys.version.split()[0], LG)
    row("Environnement", "TERMUX" if IS_TERMUX else ("WINDOWS" if IS_WIN else "LINUX"), LG)
    if IS_TERMUX:
        section("INFOS RÉSEAU TERMUX", LG)
        try:
            r = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                data = json.loads(r.stdout)
                for k,v in data.items(): row(k, str(v)[:60], LG)
            else: warn("termux-wifi-connectioninfo non dispo (installe termux-api)")
        except Exception as e: warn(f"termux-api: {e}")
    section("IP PUBLIQUE", LG)
    try:
        pub = requests.get("https://api.ipify.org?format=json", timeout=8).json()
        pip = pub.get("ip","N/A")
        geo = rget(f"https://ipapi.co/{pip}/json", timeout=8).json()
        row("IP publique", pip, LG)
        for f in ["country_name","city","org","asn","timezone"]:
            row(f, geo.get(f,"N/A"), LG)
    except: err("Impossible de récupérer l'IP publique.")
    pause()

# ══════════════════════════════════════════════
#  35 — WIFI SCANNER (Termux-api)
# ══════════════════════════════════════════════

def wifi_scanner():
    banner(); section("WIFI SCANNER", LG)
    if IS_TERMUX:
        print(LG + "  Utilisation de termux-wifi-scaninfo...")
        print(LG + "  Requis: pkg install termux-api && termux-setup-storage\n")
        try:
            r = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, timeout=15)
            if r.returncode == 0 and r.stdout.strip():
                networks = json.loads(r.stdout)
                section(f"RÉSEAUX TROUVÉS — {len(networks)}", LG)
                for net in networks:
                    print(LG + f"  ─── {net.get('ssid','?')} ─────")
                    row("SSID",      net.get("ssid","?"), LG)
                    row("BSSID",     net.get("bssid","?"), LG)
                    row("Signal",    f"{net.get('level','?')} dBm", LG)
                    row("Fréquence", f"{net.get('frequency','?')} MHz", LG)
                    row("Sécurité",  net.get("capabilities","?"), LG)
                    print()
            else:
                warn("termux-wifi-scaninfo a échoué.")
                print(LY + "  Assure-toi d'avoir accordé les permissions wifi à Termux.")
        except FileNotFoundError:
            warn("termux-wifi-scaninfo non trouvé.")
            print(LY + "  Installe: pkg install termux-api")
        except Exception as e: err(f"Erreur: {e}")
    elif IS_LINUX:
        print(LY + "  Scan Linux (nécessite root pour certains outils)")
        try:
            r = subprocess.run(["iwlist", "scan"], capture_output=True, text=True, timeout=15)
            if r.stdout:
                section("RÉSULTATS IWLIST", LG)
                for line in r.stdout.split("\n")[:60]:
                    if any(k in line for k in ["ESSID","Signal","Encryption","Frequency","Address"]):
                        print(LG + f"  {line.strip()}")
            else: warn("iwlist scan a renvoyé un résultat vide (root requis?)")
        except FileNotFoundError:
            warn("iwlist non trouvé — essai avec nmcli...")
            try:
                r = subprocess.run(["nmcli","dev","wifi","list"], capture_output=True, text=True, timeout=10)
                print(LG + r.stdout)
            except: warn("nmcli non disponible non plus.")
    else:
        warn("Scan WiFi non disponible sur Windows via cet outil.")
        print(LY + "  Utilise: netsh wlan show networks mode=bssid")
    pause()

# ══════════════════════════════════════════════
#  36 — LEAKCHECK API
# ══════════════════════════════════════════════

def leakcheck_api():
    banner(); section("LEAKCHECK API — 7.5B+ RECORDS", LR)
    print(LR + "  Free: 50 req/mois — Inscription: https://leakcheck.io\n")
    global LEAKCHECK_KEY
    key = LEAKCHECK_KEY.strip()
    if not key:
        warn("Aucune clé LeakCheck dans config.ini")
        key = input(LY + "  Entre ta clé (ou ENTER pour annuler) > ").strip()
        if not key: pause(); return
        save_key("leakcheck_key", key); LEAKCHECK_KEY = key
        ok("Clé sauvegardée dans config.ini")
    print(LR + "\n  1  Email\n  2  Username\n  3  Domaine\n  4  Téléphone\n  5  Crédits restants\n")
    c = input(LC + "  Choix > ").strip()
    TYPES = {"1":"email","2":"username","3":"domain","4":"phone"}
    if c == "5":
        try:
            r = requests.get("https://leakcheck.io/api/v2/query/test@test.com",
                             headers={"X-API-Key":key}, timeout=10)
            row("Crédits restants", r.headers.get("X-RateLimit-Remaining","?"), LR, LG)
            row("Limite mensuelle", r.headers.get("X-RateLimit-Limit","?"), LR)
        except Exception as e: err(f"Erreur: {e}")
        pause(); return
    if c not in TYPES: err("Option invalide."); pause(); return
    stype = TYPES[c]; query = input(LC + f"  {stype.title()} > ").strip()
    if not query: pause(); return
    spinner(f"LeakCheck {stype}: {query}...", 1.5, LR)
    try:
        r = requests.get(f"https://leakcheck.io/api/v2/query/{qenc(query)}",
                         headers={"X-API-Key":key}, params={"type":stype}, timeout=12)
        row("Crédits restants", r.headers.get("X-RateLimit-Remaining","?"), LR)
        if r.status_code == 200:
            data = r.json(); results = data.get("result",[])
            if not results: print(LG + "  [OK] Aucun résultat.")
            else:
                print(LR + f"  [!!!] {data.get('found',0)} entrée(s) trouvée(s)!\n")
                for i, entry in enumerate(results[:20], 1):
                    print(LR + f"\n  --- #{i} ---")
                    for field in ["email","username","password","hash","name","ip","phone","sources"]:
                        v = entry.get(field)
                        if v:
                            col = LR if field == "password" else LW
                            print(LR + f"  {field:<16}" + col + f" {str(v)[:70]}")
        elif r.status_code == 401: err("Clé invalide.")
        elif r.status_code == 429: warn("Rate limit atteint (50/mois sur free).")
        elif r.status_code == 404: print(LG + "  [OK] Aucun résultat.")
        else: warn(f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  37 — BREACHDIRECTORY API
# ══════════════════════════════════════════════

def breachdirectory_api():
    banner(); section("BREACHDIRECTORY API", LR)
    print(LR + "  Gratuit via RapidAPI — https://rapidapi.com/rohan-patra/api/breachdirectory\n")
    global BREACHDIR_KEY
    key = BREACHDIR_KEY.strip()
    if not key:
        warn("Aucune clé BreachDirectory dans config.ini")
        key = input(LY + "  Entre ta clé RapidAPI (ou ENTER pour annuler) > ").strip()
        if not key: pause(); return
        save_key("breachdirectory_key", key); BREACHDIR_KEY = key
        ok("Clé sauvegardée.")
    print(LR + "\n  1  Email\n  2  Username\n  3  IP\n  4  Domaine\n")
    c = input(LC + "  Choix > ").strip()
    TYPES = {"1":"email","2":"username","3":"ip","4":"domain"}
    if c not in TYPES: err("Option invalide."); pause(); return
    stype = TYPES[c]; query = input(LC + f"  {stype.title()} > ").strip()
    if not query: pause(); return
    spinner(f"BreachDirectory {stype}: {query}...", 1.5, LR)
    try:
        r = requests.get("https://breachdirectory.p.rapidapi.com/",
                         headers={"X-RapidAPI-Key":key,"X-RapidAPI-Host":"breachdirectory.p.rapidapi.com"},
                         params={"func":"auto","term":query}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            results = data if isinstance(data,list) else data.get("result",data.get("data",[]))
            if not results: print(LG + "  [OK] Aucun résultat.")
            else:
                print(LR + f"  [!!!] {len(results)} entrée(s) trouvée(s)!\n")
                for i, entry in enumerate(results[:20], 1):
                    print(LR + f"\n  --- #{i} ---")
                    if isinstance(entry, dict):
                        for f in ["title","email","username","password","hash","ip","name"]:
                            v = entry.get(f)
                            if v:
                                col = LR if f == "password" else LW
                                print(LR + f"  {f:<14}" + col + f" {str(v)[:70]}")
        elif r.status_code in [401,403]: err("Clé invalide.")
        elif r.status_code == 429: warn("Rate limit atteint.")
        else: warn(f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e: err(f"Erreur: {e}")
    pause()

# ══════════════════════════════════════════════
#  38 — OPEN SOURCE HUB
# ══════════════════════════════════════════════

def _run_tool(cmd, label, key_tool, success_markers, err_advice):
    """Lance un outil externe avec fallback si non installé."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0 and result.stdout.strip():
            section(label, LM)
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if not line: continue
                if any(m in line for m in ["[+]","[!]","FOUND","found","breaches"]): print(LG+f"  {line}")
                elif any(m in line for m in ["[-]","not","None"]): print(DIM+LW+f"  {line}")
                else: print(LM+f"  {line}")
        else: raise FileNotFoundError
    except FileNotFoundError:
        warn(f"{key_tool} non installé.")
        print(LY + f"  Install: pip install {key_tool}")
        print(LY + f"  Conseil: {err_advice}")

def holehe_tool():
    banner(); section("HOLEHE — EMAIL SUR 120+ SITES", LM)
    email = input(LM + "  Email > ").strip()
    if "@" not in email: err("Email invalide."); pause(); return
    _run_tool(["holehe", email, "--only-used"], f"HOLEHE — {email}",
              "holehe", ["[+]","used"],
              "holehe <email>  — github.com/megadose/holehe")
    section("LIENS ALTERNATIFS", LM)
    e = qenc(email); md5 = hashlib.md5(email.lower().encode()).hexdigest()
    for name,url in [
        ("Gravatar",      f"https://www.gravatar.com/avatar/{md5}"),
        ("EmailRep.io",   f"https://emailrep.io/{e}"),
        ("HaveIBeenPwned",f"https://haveibeenpwned.com/account/{e}"),
    ]: lnk(name, url)
    pause()

def sherlock_tool():
    banner(); section("SHERLOCK — USERNAME 400+ SITES", LM)
    username = input(LM + "  Username > ").strip()
    if not username: pause(); return
    _run_tool(["sherlock", username, "--print-found"],
              f"SHERLOCK — {username}", "sherlock-project",
              ["[+]"], "sherlock <username>  — github.com/sherlock-project/sherlock")
    pause()

def h8mail_tool():
    banner(); section("H8MAIL — BREACH HUNTING", LR)
    email = input(LR + "  Email > ").strip()
    if "@" not in email: err("Email invalide."); pause(); return
    _run_tool(["h8mail","-t",email], f"H8MAIL — {email}",
              "h8mail", ["FOUND","BREACH","[+]"],
              "h8mail -t <email>  — github.com/khast3x/h8mail")
    pause()

def maigret_tool():
    banner(); section("MAIGRET — USERNAME 3000+ SITES", LM)
    username = input(LM + "  Username > ").strip()
    if not username: pause(); return
    _run_tool(["maigret", username, "--print-found"],
              f"MAIGRET — {username}", "maigret",
              ["[+]","Found"], "maigret <username>  — github.com/soxoj/maigret")
    pause()

def theharvester_tool():
    banner(); section("THEHARVESTER — RECON DOMAINE", LC)
    domain = input(LC + "  Domaine > ").strip()
    if not domain: pause(); return
    sources = input(LC + "  Sources (ENTER=google,bing,crtsh) > ").strip() or "google,bing,crtsh"
    _run_tool(["theHarvester","-d",domain,"-b",sources,"-l","200"],
              f"THEHARVESTER — {domain}", "theHarvester",
              ["[*]","[+]"], "theHarvester -d <domain> -b all  — github.com/laramies/theHarvester")
    section("FALLBACK LIENS PASSIFS", LC)
    e = qenc(domain)
    for name,url in [
        ("crt.sh",         f"https://crt.sh/?q=%.{domain}"),
        ("HunterIO",       f"https://hunter.io/domain-search/{domain}"),
        ("SecurityTrails", f"https://securitytrails.com/domain/{domain}/subdomains"),
    ]: lnk(name, url)
    pause()

def open_source_hub():
    banner(); section("HUB OUTILS OPEN SOURCE", LG)
    print(LG + "  1  Holehe     — email sur 120+ sites")
    print(LG + "  2  h8mail     — breach hunting email")
    print(LG + "  3  Sherlock   — username sur 400+ sites")
    print(LG + "  4  theHarvester — recon domaine/email")
    print(LG + "  5  Maigret    — username sur 3000+ sites")
    print(LG + "  6  Installer tous d'un coup\n")
    c = input(LG + "  Choix > ").strip()
    if   c == "1": holehe_tool(); return
    elif c == "2": h8mail_tool(); return
    elif c == "3": sherlock_tool(); return
    elif c == "4": theharvester_tool(); return
    elif c == "5": maigret_tool(); return
    elif c == "6":
        section("INSTALL TOUT EN UNE COMMANDE", LG)
        print(LW + "  Copie-colle:\n")
        print(LC + "  pip install holehe h8mail sherlock-project maigret theHarvester\n")
        print(LW + "  Sur Termux:")
        print(LC + "  pip install holehe h8mail sherlock-project maigret\n")
        print(LG + "  Liens GitHub:")
        for name,url in [
            ("Holehe",       "https://github.com/megadose/holehe"),
            ("h8mail",       "https://github.com/khast3x/h8mail"),
            ("Sherlock",     "https://github.com/sherlock-project/sherlock"),
            ("theHarvester", "https://github.com/laramies/theHarvester"),
            ("Maigret",      "https://github.com/soxoj/maigret"),
        ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  39 — OPENROUTER IA
# ══════════════════════════════════════════════

OPENROUTER_BASE   = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL  = "openrouter/auto"

OPENROUTER_MODELS = {
    "1": ("openrouter/auto",                         "Auto [GRATUIT] — meilleur modèle dispo"),
    "2": ("meta-llama/llama-3.3-70b-instruct:free",  "Llama 3.3 70B  [GRATUIT] — Meta open source"),
    "3": ("mistralai/mistral-7b-instruct:free",      "Mistral 7B     [GRATUIT] — rapide"),
    "4": ("qwen/qwen2.5-72b-instruct:free",          "Qwen 2.5 72B  [GRATUIT] — très technique"),
    "5": ("deepseek/deepseek-r1:free",               "DeepSeek R1    [GRATUIT] — raisonnement"),
    "6": ("google/gemma-3-12b-it:free",              "Gemma 3 12B   [GRATUIT] — Google"),
}

def openrouter_tool():
    banner(); section("OPENROUTER IA — GRATUIT", LG)
    print(LG + "  Inscription gratuite sans CB: https://openrouter.ai\n")
    global OPENROUTER_KEY, OPENROUTER_MODEL
    key = OPENROUTER_KEY.strip()
    if not key:
        warn("Aucune clé OpenRouter dans config.ini")
        key = input(LY + "  Entre ta clé (ou ENTER pour annuler) > ").strip()
        if not key: pause(); return
        save_key("openrouter_key", key); OPENROUTER_KEY = key
        ok("Clé sauvegardée.")
    print(LG + "  Modèles disponibles:")
    for k,(m,d) in OPENROUTER_MODELS.items(): print(LG + f"  {k}  {d}")
    mc = input(LG + "\n  Modèle (ENTER=Auto) > ").strip()
    if mc in OPENROUTER_MODELS: OPENROUTER_MODEL = OPENROUTER_MODELS[mc][0]
    print(LG + f"\n  Modèle: {OPENROUTER_MODEL}")
    print(LG + "  Mode chat — tape 'exit' pour quitter\n")
    system = ("Tu es une IA intégrée dans un outil OSINT/réseau. "
              "Réponds en français, sois direct et technique. "
              "Tu peux analyser des résultats OSINT, expliquer des concepts réseau et cybersécurité.")
    history = [{"role":"system","content":system}]
    while True:
        user_input = input(LC + "  Toi > ").strip()
        if user_input.lower() in ["exit","quit","q","0"]: break
        if not user_input: continue
        history.append({"role":"user","content":user_input})
        spinner("IA réfléchit...", 1.5, LG)
        try:
            r = requests.post(f"{OPENROUTER_BASE}/chat/completions",
                              headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                              json={"model":OPENROUTER_MODEL,"max_tokens":1000,"messages":history},
                              timeout=30)
            if r.status_code == 200:
                data = r.json()
                reply = data["choices"][0]["message"]["content"].strip()
                tokens = data.get("usage",{}).get("total_tokens","?")
                history.append({"role":"assistant","content":reply})
                print(LG + f"\n  IA [{OPENROUTER_MODEL.split('/')[-1][:20]}] ({tokens} tokens):")
                print(LW + "\n".join(f"  {line}" for line in reply.split("\n")))
                print()
            elif r.status_code == 401: err("Clé invalide."); break
            elif r.status_code == 429: warn("Rate limit. Réessaie dans quelques secondes.")
            else: err(f"HTTP {r.status_code}: {r.text[:100]}"); break
        except requests.exceptions.ConnectionError: err("Connexion impossible."); break
        except Exception as e: err(f"Erreur: {e}"); break
    pause()

# ══════════════════════════════════════════════
#  40 — API KEY MANAGER
# ══════════════════════════════════════════════

def api_key_manager():
    banner(); section("GESTIONNAIRE CLÉS API", LG)
    global LEAKCHECK_KEY,BREACHDIR_KEY,SHODAN_KEY,HUNTER_KEY,VIRUSTOTAL_KEY,OPENROUTER_KEY
    keys = [
        ("LeakCheck",       "leakcheck_key",       LEAKCHECK_KEY,  "https://leakcheck.io"),
        ("BreachDirectory", "breachdirectory_key",  BREACHDIR_KEY,  "https://rapidapi.com/rohan-patra/api/breachdirectory"),
        ("Shodan",          "shodan_key",            SHODAN_KEY,     "https://account.shodan.io/register"),
        ("Hunter.io",       "hunter_key",            HUNTER_KEY,     "https://hunter.io"),
        ("VirusTotal",      "virustotal_key",        VIRUSTOTAL_KEY, "https://www.virustotal.com"),
        ("OpenRouter",      "openrouter_key",        OPENROUTER_KEY, "https://openrouter.ai"),
    ]
    section("STATUT CLÉS", LG)
    print(LG + f"  {'SERVICE':<22} {'STATUT':<15} {'URL'}")
    print(LG + "  " + "─"*70)
    for name,cfg_name,val,url in keys:
        if val:
            masked = val[:4]+"****"+val[-4:] if len(val)>8 else "****"
            print(LG + f"  {name:<22} [OK] {masked:<12} " + DIM + url)
        else:
            print(LY + f"  {name:<22} " + LR + "[MANQUANTE]    " + DIM + url)
    print(LW + "\n  1  Ajouter/modifier clé\n  2  Voir config.ini\n  3  Réinitialiser\n")
    c = input(LG + "  Choix > ").strip()
    if c == "1":
        for i,(name,cfg_name,val,url) in enumerate(keys,1):
            print(f"  {i}  {name:<22} " + (LG+"[OK]" if val else LR+"[VIDE]"))
        try:
            idx = int(input(LG + "\n  Numéro > ").strip()) - 1
            if not 0 <= idx < len(keys): err("Numéro invalide."); pause(); return
            name,cfg_name,old_val,url = keys[idx]
            print(LY + f"\n  Service: {name}")
            print(LY + f"  URL:     {url}")
            new_key = input(LG + f"\n  Nouvelle clé {name} > ").strip()
            if not new_key: pause(); return
            save_key(cfg_name, new_key)
            if cfg_name == "leakcheck_key":       LEAKCHECK_KEY  = new_key
            elif cfg_name == "breachdirectory_key": BREACHDIR_KEY = new_key
            elif cfg_name == "shodan_key":         SHODAN_KEY     = new_key
            elif cfg_name == "hunter_key":         HUNTER_KEY     = new_key
            elif cfg_name == "virustotal_key":     VIRUSTOTAL_KEY = new_key
            elif cfg_name == "openrouter_key":     OPENROUTER_KEY = new_key
            ok(f"Clé {name} sauvegardée — active immédiatement.")
        except (ValueError,IndexError): err("Entrée invalide.")
    elif c == "2":
        try:
            with open(CONFIG_FILE,"r",encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k,_,v = line.partition("="); v = v.strip()
                        v_disp = v[:4]+"****"+v[-4:] if v and len(v)>8 else ("****" if v else "(vide)")
                        print(LC + f"  {k.strip():<25} = {v_disp}")
                    else: print(DIM+LW + f"  {line.rstrip()}")
        except Exception as ex: err(f"Erreur: {ex}")
    elif c == "3":
        confirm = input(LR + "  Réinitialiser? Toutes les clés effacées. [oui/non] > ").lower()
        if confirm == "oui":
            with open(CONFIG_FILE,"w",encoding="utf-8") as f: f.write(CONFIG_TEMPLATE)
            LEAKCHECK_KEY=BREACHDIR_KEY=SHODAN_KEY=HUNTER_KEY=VIRUSTOTAL_KEY=OPENROUTER_KEY=""
            ok("Config réinitialisée.")
    pause()

# ══════════════════════════════════════════════
#  41 — SHODAN LINKS
# ══════════════════════════════════════════════

def shodan_links():
    banner(); section("SHODAN & INTEL PLATFORMS", LC)
    target = input(LC + "  IP ou domaine > ").strip()
    e = qenc(target)
    for name,url in [
        ("Shodan host",   f"https://www.shodan.io/host/{target}"),
        ("Shodan search", f"https://www.shodan.io/search?query={e}"),
        ("Shodan domain", f"https://www.shodan.io/domain/{target}"),
        ("Censys",        f"https://search.censys.io/search?resource=hosts&q={e}"),
        ("ZoomEye",       f"https://www.zoomeye.org/searchResult?q={e}"),
        ("Greynoise",     f"https://viz.greynoise.io/ip/{target}"),
        ("FOFA",          f"https://fofa.info/result?qbase64={base64.b64encode(target.encode()).decode()}"),
        ("BinaryEdge",    f"https://app.binaryedge.io/services/query?query={e}"),
        ("OTX",           f"https://otx.alienvault.com/indicator/domain/{target}"),
        ("VirusTotal",    f"https://www.virustotal.com/gui/domain/{target}"),
        ("URLScan",       f"https://urlscan.io/search/#{e}"),
    ]: lnk(name, url)
    pause()

# ══════════════════════════════════════════════
#  99 — CONTACT
# ══════════════════════════════════════════════

def contact():
    banner(); section("CONTACT — By camzzz", LG)
    print(LC + """
  ╔──────────────────────────────────────────────╗
  │  Discord   : cameleonmortis                  │
  │  GitHub    : github.com/cameleonnbss         │
  │  Tool      : CAMZZZ MULTI-TOOL V8            │
  │  Edition   : Termux / Android / Linux        │
  ╚──────────────────────────────────────────────╝
""")
    for line in CAMZZZ_LINES: rainbow(line)
    print(); pause()

# ══════════════════════════════════════════════
#  MENU PRINCIPAL
# ══════════════════════════════════════════════

MENU = f"""
{LC}┌─────────────── {LY} RÉSEAU/IP{LC} ─────────────────┐  {LC}┌─────────────── {LY} WEB{LC} ──────────────────────┐
{LC}│ {LG}01{LW} IP Info & Tracker                    {LC}│  {LC}│ {LG}07{LW} HTTP Header Inspector              {LC}│
{LC}│ {LG}02{LW} DNS Lookup (DoH, 10 types)           {LC}│  {LC}│ {LG}08{LW} SSL Certificate Inspector          {LC}│
{LC}│ {LG}03{LW} WHOIS / Reverse DNS                  {LC}│  {LC}│ {LG}09{LW} Technology Detector (30+ CMS)      {LC}│
{LC}│ {LG}04{LW} Port Scanner (top ports / custom)    {LC}│  {LC}│ {LG}10{LW} URL Redirect Tracer               {LC}│
{LC}│ {LG}05{LW} Subdomain Finder (130+ wordlist)     {LC}│  {LC}│ {LG}11{LW} WAF / Firewall Detector           {LC}│
{LC}│ {LG}06{LW} ASN / BGP Lookup                     {LC}│  {LC}│ {LG}18{LW} Robots / Sitemap Reader          {LC}│
{LC}└─────────────────────────────────────────────┘  {LC}│ {LG}19{LW} Wayback Machine                {LC}│
                                                   {LC}│ {LG}20{LW} Google Dork Generator          {LC}│
{LC}┌─────────────── {LY} OSINT{LC} ────────────────────┐  {LC}│ {LG}21{LW} Advanced Dork Builder         {LC}│
{LC}│ {LG}22{LW} OSINT Dork Builder (personne)        {LC}│  {LC}│ {LG}41{LW} Shodan & Intel Platforms      {LC}│
{LC}│ {LG}23{LW} Phone Number Info + OSINT            {LC}│  {LC}└─────────────────────────────────────────┘
{LC}│ {LG}24{LW} Email / Mail OSINT                   {LC}│
{LC}│ {LG}25{LW} Username Tracker (60+ sites)         {LC}│  {LC}┌─────────────── {LY} HASH / PASSWORD{LC} ────────┐
{LC}│ {LG}28{LW} Profile Builder                      {LC}│  {LC}│ {LG}29{LW} Hash Tools (générer/cracker)     {LC}│
{LC}│ {LG}32{LW} Reverse Image Search                 {LC}│  {LC}│ {LG}30{LW} Password Tools (générer/tester)  {LC}│
{LC}│ {LG}33{LW} Quick Recon (tout-en-un)             {LC}│  {LC}│ {LG}31{LW} Metadata Extractor (GPS EXIF)    {LC}│
{LC}│ {LG}34{LW} Network Info (local + public)        {LC}│  {LC}└─────────────────────────────────────────┘
{LC}└─────────────────────────────────────────────┘
                                                   {LC}┌─────────────── {LY}🛠️  AVANCÉ / TERMUX{LC} ──────────┐
{LC}┌─────────────── {LY} BREACH / LEAK{LC} ────────────┐  {LC}│ {LG}12{LW} Traceroute (Termux compatible)  {LC}│
{LC}│ {LG}26{LW} Breach Search Engine                 {LC}│  {LC}│ {LG}13{LW} Banner Grabber                  {LC}│
{LC}│ {LG}27{LW} XposedOrNot API [GRATUIT, sans clé]  {LC}│  {LC}│ {LG}14{LW} MAC Vendor Lookup               {LC}│
{LC}│ {LG}36{LW} LeakCheck API [7.5B+, clé gratuite]  {LC}│  {LC}│ {LG}15{LW} HTTP Method Tester              {LC}│
{LC}│ {LG}37{LW} BreachDirectory API [RapidAPI free]  {LC}│  {LC}│ {LG}16{LW} CORS Checker                    {LC}│
{LC}└─────────────────────────────────────────────┘  {LC}│ {LG}17{LW} TOR Exit Node Check             {LC}│
                                                   {LC}│ {LG}35{LW} WiFi Scanner (Termux-API)        {LC}│
{LC}┌─────────────── {LY} OPEN SOURCE{LC} ─────────────┐  {LC}└─────────────────────────────────────────┘
{LC}│ {LG}80{LW} Hub Outils Open Source               {LC}│
{LC}│ {LG}81{LW} Holehe  (email 120+ sites)           {LC}│  {LC}┌─────────────── {LY} EXTRA{LC} ─────────────────┐
{LC}│ {LG}82{LW} h8mail  (breach hunting)             {LC}│  {LC}│ {LG}90{LW} OpenRouter IA [GRATUIT]          {LC}│
{LC}│ {LG}83{LW} Sherlock (username 400+)             {LC}│  {LC}│ {LG}98{LW} Gestionnaire Clés API            {LC}│
{LC}│ {LG}84{LW} theHarvester (recon domaine)         {LC}│  {LC}│ {LG}99{LW} Contact                         {LC}│
{LC}│ {LG}85{LW} Maigret (username 3000+)             {LC}│  {LC}│ {LG}00{LW} Quitter                         {LC}│
{LC}└─────────────────────────────────────────────┘  {LC}└─────────────────────────────────────────┘

  {LR}[!]{LW} Usage éducatif et autorisé uniquement  {DIM}— github.com/cameleonnbss
"""

DISPATCH = {
    "01":ip_info,      "1":ip_info,
    "02":dns_lookup,   "2":dns_lookup,
    "03":whois_reverse,"3":whois_reverse,
    "04":port_scanner, "4":port_scanner,
    "05":subdomain_finder,"5":subdomain_finder,
    "06":asn_lookup,   "6":asn_lookup,
    "07":header_inspector,"7":header_inspector,
    "08":ssl_inspector,"8":ssl_inspector,
    "09":tech_detector,"9":tech_detector,
    "10":url_tracer,
    "11":waf_detector,
    "12":traceroute,
    "13":banner_grab,
    "14":mac_lookup,
    "15":http_method_tester,
    "16":cors_checker,
    "17":tor_check,
    "18":robots_sitemap,
    "19":wayback,
    "20":dork_gen,
    "21":adv_dork,
    "22":osint_dork_builder,
    "23":phone_info,
    "24":mail_osint,
    "25":username_tracker,
    "26":breach_engine,
    "27":xposedornot,
    "28":profile_builder,
    "29":hash_tools,
    "30":password_tools,
    "31":metadata_extractor,
    "32":reverse_image,
    "33":quick_recon,
    "34":network_info,
    "35":wifi_scanner,
    "36":leakcheck_api,
    "37":breachdirectory_api,
    "41":shodan_links,
    "80":open_source_hub,
    "81":holehe_tool,
    "82":h8mail_tool,
    "83":sherlock_tool,
    "84":theharvester_tool,
    "85":maigret_tool,
    "90":openrouter_tool,
    "98":api_key_manager,
    "99":contact,
    # Aliases social/osint
    "social":social_search,
    "paste":paste_search,
    "dark":darkweb_search,
    "vuln":vuln_search,
    "archive":archive_links,
    "file":file_osint,
    "camera":public_cameras,
    "osint":osint_framework,
}

# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

if __name__ == "__main__":
    try:
        intro()
        while True:
            clear()
            banner()
            print(MENU)
            choice = input(LG + "  Sélectionne un module > ").strip().lower()
            if choice in ["0","00","exit","quit","q"]:
                clear()
                for line in CAMZZZ_LINES: rainbow(line)
                print()
                print(LG + "  Goodbye — By camzzz — V8 Termux Edition")
                time.sleep(0.8); break
            fn = DISPATCH.get(choice)
            if fn:
                try: fn()
                except KeyboardInterrupt: print(LY + "\n  Interrompu."); time.sleep(0.3)
                except Exception as e:
                    err(f"Erreur dans le module: {e}")
                    time.sleep(1)
            else:
                print(LR + f"  Option invalide: '{choice}'"); time.sleep(0.5)
    except KeyboardInterrupt:
        print(LY + "\n\n  Ctrl+C — Au revoir!")
