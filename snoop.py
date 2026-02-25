#! /usr/bin/env python3
# Copyright (c) 2020 Snoop Project <snoopproject@protonmail.com>

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import argparse
import certifi
import csv
import glob
import itertools
import json
import locale
import os
import platform
import psutil
import random
import re
import requests
import shutil
import signal
import ssl
import subprocess
import sys
import textwrap
import time
import webbrowser

from charset_normalizer import detect as char_detect
from collections import Counter
from colorama import Fore, init, Style
from concurrent.futures import as_completed, ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError
from multiprocessing import active_children, set_start_method
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TimeElapsedColumn
from rich.style import Style as STL
from rich.table import Table

import snoopbanner
import snoopnetworktest
import snoopplugins

if int(platform.python_version_tuple()[1]) >= 8:
    from importlib.metadata import version as version_lib
    PYTHON_3_8_PLUS = True
else:
    PYTHON_3_8_PLUS = False


locale.setlocale(locale.LC_ALL, '')
init(autoreset=True)
console = Console()


def premium():
    pass


def meta(cert=False):
    pass


## Banner and software version.
def version_snoop(vers, vers_code, demo_full):
    print(f"""\033[36m
  ___|
\\___ \\  __ \\   _ \\   _ \\  __ \\ 
      | |   | (   | (   | |   | 
_____/ _|  _|\\___/ \\___/  .__/  
                         _|    \033[0m \033[37m\033[44m{vers}\033[0m
""")

    sb = "build" if vers_code == 'b' else "source"
    _sb = "demo" if demo_full == 'd' else "full"

    if WINDOWS: OS_ = f"Snoop for Windows {sb} {_sb}"
    elif ANDROID: OS_ = f"Snoop for Termux {sb} {_sb}"
    elif LINUX: OS_ = f"Snoop for GNU/Linux {sb} {_sb}"

    console.print(f"[dim cyan]Examples:\n $ [/dim cyan]" + \
                  f"[cyan]{'cd C:' + chr(92) + 'path' + chr(92) + 'snoop' if WINDOWS else 'cd ~/snoop'}[/cyan]")
    console.print(f"[dim cyan] $ [/dim cyan][cyan]{'python' if WINDOWS else 'python3'} snoop.py --help[/cyan] #help")
    console.print(f"[dim cyan] $ [/dim cyan][cyan]{'python' if WINDOWS else 'python3'} snoop.py --module[/cyan] #plugins")
    console.print(f"[dim cyan] $ [/dim cyan][cyan]{'python' if WINDOWS else 'python3'} snoop.py nickname[/cyan] #search user")
    console.rule(characters="=", style="cyan")
    print("")

    return f"{vers}_{OS_}"


## Create result directories.
def mkdir_path():
    try:
        if not WINDOWS and "build" in VERSION:
            replace_snoop_dir = os.path.join(os.environ["HOME"], 'snoop')
            if os.path.exists(replace_snoop_dir):
                shutil.move(replace_snoop_dir, os.path.join(os.environ["HOME"], '.snoop'))
    except Exception:
        pass

    dirhome = os.path.join(os.environ["LOCALAPPDATA" if WINDOWS else "HOME"], "snoop" if WINDOWS else '.snoop')

    if ANDROID:
        if not os.access("/data/data/com.termux/files/home/storage/shared", os.W_OK):
            console.print("[bold yellow]Agree to a one-time, standard operation in Termux, granting disk access, " + \
                          "otherwise search results cannot be saved in a public directory on Android OS, " + \
                          "see Wiki Termux for details: https://wiki.termux.com/wiki/Termux-setup-storage[/bold yellow]\n")
            code = subprocess.run("termux-setup-storage", shell=True)
            if code.returncode == 1:
                console.print("\n[bold red]search results directory: '/storage/emulated/0/snoop' not created, " + \
                              "declined by user.[bold red]\n")
        else:
            dirhome = "/data/data/com.termux/files/home/storage/shared/snoop"

    dirpath = os.getcwd() if 'source' in VERSION and not ANDROID else dirhome

    os.makedirs(f"{dirpath}/results", exist_ok=True)
    os.makedirs(f"{dirpath}/results/nicknames/html", exist_ok=True)
    os.makedirs(f"{dirpath}/results/nicknames/txt", exist_ok=True)
    os.makedirs(f"{dirpath}/results/nicknames/csv", exist_ok=True)
    os.makedirs(f"{dirpath}/results/nicknames/save reports", exist_ok=True)
    os.makedirs(f"{dirpath}/results/plugins/ReverseVgeocoder", exist_ok=True)
    os.makedirs(f"{dirpath}/results/plugins/Yandex_parser", exist_ok=True)
    os.makedirs(f"{dirpath}/results/plugins/domain", exist_ok=True)

    return dirpath


## Constants.
ANDROID = True if hasattr(sys, 'getandroidapilevel') else False
WINDOWS = True if sys.platform == 'win32' else False
LINUX = True if ANDROID is False and WINDOWS is False else False
MACOS = True if platform.system() == "Darwin" else False #macOS support (experimental).

E_MAIL = 'demo: snoopproject@protonmail.com'
END_OF_LICENSE = (2027, 1, 1, 3, 0, 0, 0, 0, 0) #date format according to ISO 8601: year-month-day.
VERSION = version_snoop('v1.4.3', "s", "f")
DIRPATH = mkdir_path()
TIME_START = time.time()
TIME_DATE = time.localtime()


dic_binding = {"badraw": [], "badzone": [],
               "censors": 0, "android_lame_workhorse": False}


## Create web directory and control it, but not files inside + set correct permissions "-x -R" after compiling binary data [.mp3].
def web_path_copy():
    try:
        if "build" in VERSION and os.path.exists(f"{DIRPATH}/web") is False:
            shutil.copytree(web_path, f"{DIRPATH}/web")
            if LINUX: #and 'build' in 'VERSION'
                os.chmod(f"{DIRPATH}/web", 0o755)
                for total_file_path in glob.iglob(f"{DIRPATH}/web/**/*", recursive=True):
                    if os.path.isfile(total_file_path) == True:
                        os.chmod(total_file_path, 0o644)
                    else:
                        os.chmod(total_file_path, 0o755)
        elif "source" in VERSION and ANDROID and os.path.exists("/data/data/com.termux/files/home/storage/shared/snoop/web") is False:
            shutil.copytree(f"{os.getcwd()}/web", "/data/data/com.termux/files/home/storage/shared/snoop/web")
    except Exception as e:
        print(f"ERR: {e}")


## License validity.
def license():
    date_up = int(time.mktime(END_OF_LICENSE)) #date in seconds since epoch
    End = time.strftime('%Y-%m-%d', time.gmtime(date_up))

    if time.time() > date_up:
        snoopbanner.logo(text=f"Software {VERSION} deactivated per license.")
        sys.exit()

    return End


## Memory usage.
def mem_test():
    try:
        return round(psutil.virtual_memory().available / 1024 / 1024)
    except Exception:
        if not WINDOWS:
            console.print(f"{' ' * 17} [bold red]ERR Psutil lib[/bold red]")
            return int(subprocess.check_output("free -m", shell=True, text=True).splitlines()[1].split()[-1])
        else:
            return -1


## Print info string.
def info_str(infostr, nick, color=True):
    if color is True:
        print(f"{Fore.GREEN}[{Fore.YELLOW}*{Fore.GREEN}] {infostr}{Fore.RED} <{Fore.WHITE} {nick} {Fore.RED}>{Style.RESET_ALL}")
    else:
        print(f"\n[*] {infostr} < {nick} >")


## Username validation.
with open('domainlist.txt', 'r', encoding="utf-8") as err:
    ERMAIL_SET = set(line.strip() for line in err if line.strip())
def check_invalid_username(username, symbol_bad_username=None, phone=None, dot=None, email=None):
    if symbol_bad_username: #check username for special characters
        symbol_bad = re.compile(r"[^a-zA-Z\_\s\d\%\@\-\.\+]")
        err_nick = re.findall(symbol_bad, username)

        if err_nick:
            print(Style.BRIGHT + Fore.RED + format_txt("⛔️ invalid characters in nickname: " + \
                                                       "{0}{1}{2}{3}{4}".format(Style.RESET_ALL, Fore.RED, err_nick,
                                                                                Style.RESET_ALL, Style.BRIGHT + Fore.RED),
                                                       k=True, m=True) + "\n   skipping\n")
            return False

    if phone: #check username for phone number
        patterns = {'Russia/Kazakhstan': r'^(?:\+7|7|8)\d{10}$', 'Belarus': r'^(?:\+375|375|80)\d{9}$',
                    'Ukraine': r'^(?:\+380|380)\d{9}$', 'EU/CIS/AU/SA': r'^(?:0)\d{9}$',
                    'Uzbekistan': r'^(?:\+998|998)\d{9}$', 'Tajikistan': r'^(?:\+992|992)\d{9}$',
                    'Kyrgyzstan': r'^(?:\+996|996|0)\d{9}$', 'Armenia': r'^(?:\+374|374)\d{8}$',
                    'Azerbaijan': r'^(?:\+994|994)\d{9}$', 'Moldova': r'^(?:\+373|373)\d{8}$',
                    'Georgia': r'^(?:\+995|995)\d{9}$', 'Turkmenistan': r'^(?:\+993|993)\d{8}$',
                    'United Kingdom': r'^(?:\+44|44)\d{10}$', 'Hungary': r'^\+36\d{9}$',
                    'Cyprus': r'^(?:\+357|357)\d{8}$', 'Latvia': r'^(?:\+371|371)\d{8}$',
                    'Lithuania': r'^(?:\+370|370)\d{8}$', 'Netherlands': r'^(?:\+31|31)\d{9}$',
                    'Norway': r'^(?:\+47|47)\d{8}$', 'Poland': r'^(?:\+48|48)\d{9}$',
                    'Portugal': r'^(?:\+351|351)\d{9}$', 'Romania': r'^(?:\+40|40)\d{9}$',
                    'Slovakia': r'^(?:\+421|421)\d{9}$', 'Slovenia': r'^(?:\+386|386)\d{8}$',
                    'Turkey': r'^(?:\+90|90)\d{10}$', 'France': r'^(?:\+33|33)\d{9}$',
                    'Czechia': r'^(?:\+420|420)\d{9}$', 'Switzerland': r'^(?:\+41|41)\d{9}$',
                    'USA/Canada': r'^(?:\+1|1)\d{10}$', 'Australia': r'^(?:\+61|61)\d{9}$',
                    'India': r'^(?:\+91|91)\d{10}$', 'China': r'^(?:\+86|86)?\d{11}$',
                    'Japan': r'^(?:\+81|81)\d{10}$', 'Mexico': r'^(?:\+52|52)?\d{10}$', 
                    'South Africa': r'^(?:\+27|27)\d{9}$'}
        
        for country, pattern in patterns.items():
            if re.match(pattern, username):
                print(Style.BRIGHT + Fore.RED + format_txt("⛔️ snoop tracks user accounts, " + \
                                                           "not phone numbers; detected phone number from location: '{0}'"
                                                           .format(country), k=True, m=True) + "\n   skipping\n")
                return False

    if dot: #check username for dot/email
        if username.count(".") > 1:
            print(Style.BRIGHT + Fore.RED + format_txt("⛔️ nickname containing more than one [.] is restricted for search, " + \
                                                       "reason: high complexity of DB support...",
                                                       k=True, m=True) + "\n   skipping\n")
            return False

    if email: #check username for e_mail
        username_bad = username.rsplit(sep='@', maxsplit=1)
        username_bad = '@bro'.join(username_bad).lower()

        for ermail_iter in ERMAIL_SET:
            if ermail_iter.lower() == username.lower():
                print("\n" + Style.BRIGHT + Fore.RED + format_txt("⛔️ bad nickname: '{0}' (bare domain detected)"
                                                                  .format(ermail_iter), k=True, m=True) + "\n   skipping\n")
                return False
            elif ermail_iter.lower() in username.lower():
                usernameR = username.rsplit(sep=ermail_iter.lower(), maxsplit=1)[1]
                username = username.rsplit(sep='@', maxsplit=1)[0]

                if len(username) == 0:
                    username = usernameR
                print(f"\n{Fore.CYAN}E-mail address detected, extracting nickname: " + \
                      f"'{Style.BRIGHT}{Fore.CYAN}{username}{Style.RESET_ALL}" + \
                      f"{Fore.CYAN}'\nSnoop can distinguish e-mail from login, for example, searching '{username_bad}'\n" + \
                      f"is not a valid email, but may exist as a nickname, therefore — it will not be trimmed\n")

                if len(username) != 0 and len(username) < 3:
                    print(Style.BRIGHT + Fore.RED + format_txt("⛔️ nickname cannot be shorter than 3 characters",
                                                               k=True, m=True) + "\n   skipping\n")
                    return False

    return username


## Bad_raw, bad_zone.
def bad_raw(flagBS_err, bad_zone, nick, lst_options):
    print(f"{Fore.CYAN}├───Search date:{Style.RESET_ALL} {time.strftime('%Y-%m-%d__%H:%M:%S', TIME_DATE)}")

    if any(lst_options):
        print(f"{Fore.CYAN}└────\033[31;1mBad_raw: {flagBS_err}% DB, bad_zone {bad_zone}\033[0m\n")
    else:
        if 4 >= flagBS_err >= 2:
            print(f"{Fore.CYAN}└────\033[33;1mWarning! Bad_raw: {flagBS_err}% DB, bad_zone {bad_zone}\033[0m")
        elif 12 >= flagBS_err > 4:
            print(f"{Fore.CYAN}└────\033[31;1mWarning!! Bad_raw: {flagBS_err}% DB, bad_zone {bad_zone}\033[0m")
        elif flagBS_err > 12:
            print(f"{Fore.CYAN}└────\033[30m\033[41mWarning!!! Bad_raw: {flagBS_err}% DB, critical level, " + \
                  f"bad_zone {bad_zone}\033[0m")

    if not any(lst_options):
        print(Fore.CYAN + "     └─unstable connection or I_Censorship")
        print(f"       \033[36m{'├' if 'full' in VERSION else '└'}─use \033[36;1mVPN\033[0m\033[36m/'\033[0m" + \
              f"\033[36;1m--web-base\033[0m\033[36m'\033[0m ", end='' if 'full' in VERSION else '\n\n')
        if "full" in VERSION:
            nick = f"'{nick}'" if nick.count(" ") > 0 else nick
            print(f"\033[36m\n       └─or exclude from search bad_zone: '\033[36;1m" + \
                  f"{bad_zone.split('/')[0].replace('~', '')}\033[0m" + \
                  f"\033[36m'\n         └─$ {os.path.basename(sys.argv[0])} -w --exclude " + \
                  f"{bad_zone.split('/')[0].replace('~', '')} {nick}\033[0m\n")


## Formatting, indentation.
def format_txt(text, k=False, m=False):
    """
    Some consoles on Windows do not support the "•" symbol, 'subprocess.run' — on some versions of Windows
    works in a different encoding/font from the default. A more reliable solution would be to check characters
    via a temporary change of the 'io' stream, but then the colors in the console will break. The rest of the code regulates the indentations.
    """
    if WINDOWS:
        try:
            for symbol in ["•", "·", "*", "-", "+"]:
                check_symbol = subprocess.run(['cmd.exe', '/c', 'echo', symbol], capture_output=True, text=True).stdout.strip()
                if symbol in check_symbol:
                    break
        except Exception:
            symbol = "+"

    gal = f" {symbol} " if WINDOWS else " ✔ "
    indent_end = "" if k else " " * 3
    gal = gal if k and not m else ""

    try:
        return textwrap.fill(f"{gal}{text}", width=os.get_terminal_size()[0], subsequent_indent=" " * 3, initial_indent=indent_end)
    except OSError:
        return textwrap.fill(f"{gal}{text}", width=80, subsequent_indent=" " * 3, initial_indent=indent_end)


## Print errors.
def print_error(websites_names, errstr, country_code, errX, verbose=False, color=True, idx=""):
    """Print various types of network errors."""
    prefix = f"#{idx}::::::::::" if idx else ""
    if color is True:
        print(f"{prefix}{Style.RESET_ALL}{Fore.RED}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.RED}]{Style.BRIGHT}" \
              f"{Fore.GREEN} {websites_names}: {Style.BRIGHT}{Fore.RED}{errstr}{country_code}" \
              f"{Fore.YELLOW} {errX if verbose else ''} {Style.RESET_ALL}")
    else:
        print(f"{prefix}[!] {websites_names}: {errstr}{country_code} {errX if verbose else ''}")


## Print output on different platforms, indication.
def print_found_country(websites_names, url, country_Emoj_Code, verbose=False, color=True, idx=""):
    """Print account found."""
    prefix = f"#{idx}::::::::::" if idx else ""
    if color is True and WINDOWS:
        print(f"{prefix}{Style.RESET_ALL}{Style.BRIGHT}{Fore.CYAN}{country_Emoj_Code}" \
              f"{Fore.GREEN}  {websites_names}:{Style.RESET_ALL}{Fore.GREEN} {url}{Style.RESET_ALL}")
    elif color is True and not WINDOWS:
        print(f"{prefix}{Style.RESET_ALL}{country_Emoj_Code}{Style.BRIGHT}{Fore.GREEN}  {websites_names}: " \
              f"{Style.RESET_ALL}{Style.DIM}{Fore.GREEN}{url}{Style.RESET_ALL}")
    else:
        print(f"{prefix}[+] {websites_names}: {url}")


def print_not_found(websites_names, verbose=False, color=True, idx=""):
    """Print account not found."""
    prefix = f"#{idx}::::::::::" if idx else ""
    if color is True:
        print(f"{prefix}{Style.RESET_ALL}{Fore.CYAN}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.CYAN}]" \
              f"{Style.BRIGHT}{Fore.GREEN} {websites_names}: {Style.BRIGHT}{Fore.YELLOW}Alas!{Style.RESET_ALL}")
    else:
        print(f"{prefix}[-] {websites_names}: Alas!")


## Print skipped sites by block. mask in username, gray_list.
def print_invalid(websites_names, message, color=True, idx=""):
    prefix = f"#{idx}::::::::::" if idx else ""
    if color is True:
        return f"{prefix}{Style.RESET_ALL}{Fore.RED}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.RED}]" \
               f"{Style.BRIGHT}{Fore.GREEN} {websites_names}: {Style.RESET_ALL}{Fore.YELLOW}{message}{Style.RESET_ALL}\n"
    else:
        return f"{prefix}[-] {websites_names}: {message}\n"


## Print warning about outdated library versions.
def warning_lib():
    if int(requests.urllib3.__version__.split(".")[0]) < 2 or int("".join(requests.__version__.split("."))) < 2282:
        console.log("[yellow]Warning! \n\nIn Requests > v2.28.2 / Urllib3 v2 developers dropped support for older ciphers. " + \
                    "Some, few, outdated sites from the DB working on old technology will continue " + \
                    "connecting without errors (Snoop will strive to provide compatibility mode with any older versions " + \
                    "Requests / Urllib3).[/yellow]\n\n[bold green]It is still recommended to update dependencies: \n" + \
                    "$ python -m pip install requests urllib3 -U[/bold green]", highlight=False)
        console.rule(characters="=", style="cyan")


## Network.
def r_session(cert=False, connect=0, speed=False, norm = False, method="get",
              url=None, headers="", allow_redirects=True, req_retry=False, timeout=9):
    """
    The session object is needed to expand the pool of network connections, significant minus (multithreading/OS Windows):
    over time, CPU time leaks. Workaround: create a temporary session for each connection without caching,
    performance gain (Windows) ~25-30%.
    Also, in urllib3 version > 2 with multiprocessing (Linux), it is necessary to manually pickle the SSL object.
    """

    if speed:
        connections = (speed + 20) if speed >= 60 else (70 if not WINDOWS else 50)
    elif speed is False:
        connections = 200 if LINUX else (70 if WINDOWS else 40) #L/W/A.

    if req_retry:
        total = False if norm else None
        retry = requests.urllib3.util.Retry(total=100, connect=100, read=100, status=100, other=100, backoff_factor=0.1)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    else:
        adapter = requests.adapters.HTTPAdapter()

    try: #urllib3 > 2
        cert_reqs = ssl.CERT_NONE if cert is False else ssl.CERT_REQUIRED
        ciphers = 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:ECDH+AESGCM:DH+AESGCM\
                   :ECDH+AES:DH+AES:RSA+AESGCM:RSA+AES:!aNULL:!eNULL:!MD5:!DSS:HIGH:!DH'
        ctx = requests.urllib3.util.create_urllib3_context(ciphers=ciphers, cert_reqs=cert_reqs)
        adapter.init_poolmanager(connections=connections, maxsize=40 if ANDROID else 20, block=False,
                                 ssl_minimum_version=ssl.TLSVersion.TLSv1, ssl_context=ctx)
    except Exception: #urllib3 < 2, no need to reconfigure processes
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        adapter.init_poolmanager(connections=connections, maxsize=20, block=False)

    requests.packages.urllib3.disable_warnings()
    r_session = requests.Session()
    r_session.max_redirects = 6 if ANDROID else 9
    r_session.verify = False if cert is False else certifi.where()
    r_session.mount('http://', adapter)
    r_session.mount('https://', adapter)

    if method == "get":
        req_session = r_session.get
    elif method == "head":
        req_session = r_session.head

    return req_session(url=url, headers=headers, allow_redirects=allow_redirects, timeout=timeout)


## Return future result.
# Logic: return response and duplicate method (out of 4) in case of success/retry.
def r_results(request_future, error_type, websites_names, timeout=None, norm=False,
              print_found_only=False, verbose=False, color=True, country_code='', idx=""):
    try:
        res = request_future.result(timeout=timeout + 10)
        if res.status_code:
            return res, error_type, str(round(res.elapsed.total_seconds(), 2))
    except requests.exceptions.HTTPError as err1:
        if norm is False and print_found_only is False:
            print_error(websites_names, "HTTP Error ", country_code, err1, verbose, color, idx)
    except requests.exceptions.ConnectionError as err2:
        if norm is False and ('aborted' in str(err2) or 'None: None' in str(err2) or
                              'SSLZeroReturnError' in str(err2) or 'Failed' in str(err2) or 'None' == str(err2)):
            dic_binding["censors"] += 1
            if print_found_only is False:
                print_error(websites_names, "Connection Error ", country_code, err2, verbose, color, idx)
            return "FakeNone", "", "-"
        else:
            if norm is False and print_found_only is False:
                print_error(websites_names, "Censorship | TLS ", country_code, err2, verbose, color, idx)
    except (requests.exceptions.Timeout, TimeoutError) as err3:
        if norm is False and print_found_only is False:
            print_error(websites_names, "Timeout error ", country_code, err3, verbose, color, idx)
        if len(str(repr(err3))) == 14:
            dic_binding["censors"] += 1
            return "FakeStuck", "", "-"
    except requests.exceptions.RequestException as err4:
        if norm is False and print_found_only is False:
            print_error(websites_names, "Unexpected error ", country_code, err4, verbose, color, idx)
    except Exception as err5:
        if norm is False and print_found_only is False:
            print_error(websites_names, "Network Pool Crash ", country_code, err5, verbose, color, idx)

    dic_binding["censors"] += 1

    return None, "Great Snoop returns None", "-"


## Saving reports, option (-S).
def new_session(url, headers, error_type, username, websites_names, r, t):
    """
    If the nickname is found, but the actual html-page is further down the redirect,
    we raise a new connection and move along the redirect to capture and save it.
    """

    response = r_session(url=url, headers=headers, allow_redirects=True, timeout=t)

# Trap on some sites (if response.content is not None ≠ if response.content).
    if response.content is not None and response.encoding == 'ISO-8859-1':
        try:
            response.encoding = char_detect(response.content).get("encoding")
            if response.encoding is None:
                response.encoding = "utf-8"
        except Exception:
            response.encoding = "utf-8"

    try:
        session_size = len(response.content) #counting extracted data
    except UnicodeEncodeError:
        session_size = None
    return response, session_size


def sreports(url, headers, error_type, username, websites_names, r):
    os.makedirs(f"{DIRPATH}/results/nicknames/save reports/{username}", exist_ok=True)
# Save reports for method: redirection.
    if error_type == "redirection":
        try:
            response, session_size = new_session(url, headers, error_type,
                                                 username, websites_names, r, t=6)
        except requests.exceptions.ConnectionError:
            time.sleep(0.02)
            try:
                response, session_size = new_session(url, error_type, username,
                                                     websites_names, r, headers="", t=3)
            except Exception:
                session_size = 'Err' #counting extracted data
        except Exception:
            session_size = 'Err'
# Save reports for all other methods: status; response; message with standard parameters.
    try:
        with open(f"{DIRPATH}/results/nicknames/save reports/{username}/{websites_names}.html", 'w', encoding=r.encoding) as rep:
            if 'response' in locals():
                rep.write(response.text)
            elif error_type == "redirection" and 'response' not in locals():
                rep.write("❌ Snoop Project bad_save, timeout")
            else:
                rep.write(r.text)
    except Exception:
        console.log(snoopbanner.err_all(err_="low"), f"\nlog --> [{websites_names}:[bold red] {r.encoding} | response?[/bold red]]")

    if error_type == "redirection":
        return session_size


## Snoop function.
def snoop(username, BDdemo_new, verbose=False, norm=False, reports=False, user=False, country=False, lst_username=None,
          speed=False, print_found_only=False, timeout=None, color=True, cert=False, header_custom=None, multithread=False):
## Print infostrings.
    easteregg = ['snoop', 'snoop project', 'snoop_project', 'snoop-project', 'snooppr']

    nick = username.replace("%20", " ") #username 2-variables (args/info)
    info_str("looking for:", nick, color)

    if len(username) < 3:
        print(Style.BRIGHT + Fore.RED + format_txt("⛔️ nickname cannot be shorter than 3 characters",
                                                   k=True, m=True) + "\n   skipping\n")
        return False, False, nick
    elif username.lower() in easteregg:
        with console.status("[bold blue] 💡 Easter egg detected...", spinner='noise'):
            try:
                r_east = r_session(url="https://raw.githubusercontent.com/snooppr/snoop/master/changelog.txt", timeout=timeout)
                r_repo = r_session(url='https://api.github.com/repos/snooppr/snoop', timeout=timeout).json()
                r_latestvers = r_session(url='https://api.github.com/repos/snooppr/snoop/tags', timeout=timeout).json()

                console.print(Panel(Markdown(r_east.text.replace("=" * 83, "")),
                                    subtitle="[bold blue]snoop version log[/bold blue]", style=STL(color="cyan")))
                console.print(Panel(f"[bold cyan]Project creation date:[/bold cyan] 2020-02-14 " + \
                                    f"({round((time.time() - 1581638400) / 86400)}_days).\n" + \
                                    f"[bold cyan]Last repository update:[/bold cyan] " + \
                                    f"{'_'.join(r_repo.get('pushed_at')[0:-4].split('T'))} (UTC).\n" + \
                                    f"[bold cyan]Repository compression:[/bold cyan] 2024-12-11.\n" + \
                                    f"[bold cyan]Repository size:[/bold cyan] {round(int(r_repo.get('size')) / 1024, 1)} MB.\n" + \
                                    f"[bold cyan]Github rating:[/bold cyan] {r_repo.get('watchers')} stars.\n" + \
                                    f"[bold cyan]Hidden options:[/bold cyan]\n'--headers/-H':: Set user-agent manually, agent " + \
                                                              f"is enclosed in quotes, by default a " + \
                                                              f"random or redefined user-agent from the snoop DB is set for each site.\n" + \
                                                              f"'--cert-on/-C':: Enable certificate check on servers, " + \
                                                              f"by default certificate check on servers " + \
                                                              f"is disabled, which allows processing problematic sites without errors.\n"
                                    f"[bold cyan]Latest snoop version:[/bold cyan] {r_latestvers[0].get('name')}.",
                                    style=STL(color="cyan"), subtitle="[bold blue]key indicators[/bold blue]", expand=False))
            except Exception:
                console.log(snoopbanner.err_all(err_="high"))
        sys.exit()

    username = re.sub(" ", "%20", username)


## Prevention of 'DoS' due to invalid logins; phone numbers, search errors, special characters.
    username = check_invalid_username(username, symbol_bad_username=True, phone=True, dot=True, email=True)
    if username is False:
        return False, False, nick


## Create a multithreaded/process session for all requests.
    if multithread or WINDOWS or MACOS:
        cpu = 1 if psutil.cpu_count(logical=False) == None else psutil.cpu_count(logical=False)
        if norm is False:
            thread__ = len(BDdemo_new) if len(BDdemo_new) < (cpu * 5) else (30 if cpu < 4 else 60)
        else:
            thread__ = len(BDdemo_new) if len(BDdemo_new) < (os.cpu_count() * 5) else (40 if cpu < 4 else 80)
        executor_req = ThreadPoolExecutor(max_workers=thread__ if not speed else speed)
    elif ANDROID:
        try:
            proc_ = len(BDdemo_new) if len(BDdemo_new) < 17 else 17
            executor_req = ProcessPoolExecutor(max_workers=proc_ if not speed else speed)
        except Exception:
            console.log(snoopbanner.err_all(err_="high"))
            dic_binding.update({'android_lame_workhorse': True})
            executor_req = ThreadPoolExecutor(max_workers=10 if not speed else speed)
    elif LINUX:
        try:
            if norm is False:
                proc_ = len(BDdemo_new) if len(BDdemo_new) < 70 else (50 if len(os.sched_getaffinity(0)) < 4 else 140)
            else:
                proc_ = len(BDdemo_new) if len(BDdemo_new) < 70 else (60 if len(os.sched_getaffinity(0)) < 4 else 180)
        except Exception:
            proc_ = len(BDdemo_new) if len(BDdemo_new) < 50 else 50
        executor_req = ProcessPoolExecutor(max_workers=proc_ if not speed else speed)

    if norm is False:
        executor_req_retry = ProcessPoolExecutor(max_workers=1) if not multithread and not WINDOWS and not MACOS else ThreadPoolExecutor(max_workers=1)
    if reports is True:
        executor_req_save = ProcessPoolExecutor(max_workers=2) if not multithread and not WINDOWS and not MACOS else ThreadPoolExecutor(max_workers=2)


## Analysis of all sites.
    dic_snoop_full = {}
    BDdemo_new_quick = {}
    lst_invalid = []
## Create futures for all requests. This will parallelize requests with interrupts.
    for websites_names, param_websites in BDdemo_new.items():
        results_site = {}
        results_site['flagcountry'] = param_websites.get("country")
        results_site['flagcountryklas'] = param_websites.get("country_klas")
        results_site['url_main'] = param_websites.get("urlMain")
        # username = param_websites.get("usernameON")

# Custom browser user-agent (randomly for each site), and in case of failure — permanent with extended header.
        majR = random.choice(range(101, 124, 1))
        RandHead=([f'{{"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' + \
                   f'Chrome/{majR}.0.0.0 Safari/537.36"}}',
                   f'{{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                   f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{majR}.0.0.0 Safari/537.36"}}'])
        headers = json.loads(random.choice(RandHead))

# Override/add any additional headers required for the site from the DB, or set U-A from CLI.
        if header_custom is not None:
            headers.update({"User-Agent": ''.join(header_custom)})
        elif "headers" in param_websites:
            headers.update(param_websites["headers"])
        # console.print(headers, websites_names) #check u-agents

# Skip temporarily disabled site, do not make a request if the username is not suitable for the site.
        exclusionYES = param_websites.get("exclusion")
        if exclusionYES and re.search(exclusionYES, username) or param_websites.get("bad_site") == 1:
            if exclusionYES and re.search(exclusionYES, username) and not print_found_only and not norm:
                lst_invalid.append(print_invalid(websites_names, f"#invalid nick '{nick}' for this site", color))
            results_site["exists"] = "invalid_nick"
            results_site["url_user"] = '*' * 56
            results_site['countryCSV'] = "****"
            results_site['http_status'] = '*' * 10
            results_site['session_size'] = ""
            results_site['check_time_ms'] = '*' * 15
            results_site['response_time_ms'] = '*' * 15
            results_site['response_time_site_ms'] = '*' * 25
            if param_websites.get("bad_site") == 1 and verbose and not print_found_only and not norm:
                lst_invalid.append(print_invalid(websites_names, f"*SKIP. DYNAMIC GRAY_LIST", color))
            if param_websites.get("bad_site") == 1:
                dic_binding.get("badraw").append(websites_names)
                results_site["exists"] = "gray_list"
        else:
# User URL on the site (if it exists).
            url_str = param_websites["url"]
            url = url_str.replace("{}", username).replace("{username}", username)
            results_site["url_user"] = url
            url_API = param_websites.get("urlProbe")
# Use api/nickname.
            url_API = url if url_API is None else url_API.replace("{}", username).replace("{username}", username)
# Retries.
            connect = 1 if param_websites.get("country_klas") == "UA" else 2
# If only status code is needed, do not load page body, save memory, and many protected sites prefer Head.
            if param_websites["errorType"] != 'status_code' or reports:
                method = "get"
            else:
                method = "head"
# Site redirects request.
# Forbid redirection to capture status code from initial url.
            if param_websites["errorType"] == "response_url" or param_websites["errorType"] == "redirection":
                allow_redirects = False
# Allow any redirect the site wants to make and capture body and response status.
            else:
                allow_redirects = True
# Tweak session object not for its intended purpose, rescue CPU/Windows/Multithreading over long distances.
            req_retry = True if "full" in VERSION or len(BDdemo_new) > 399 else False
# Also pickle SSL at multiprocessing.
# Send all requests in parallel and save future for later access.
            try:
                future_ = executor_req.submit(r_session, cert=cert, speed=speed, norm=norm,
                                              connect=connect, method=method, req_retry=req_retry,
                                              url=url_API, headers=headers, allow_redirects=allow_redirects, timeout=timeout)

                if norm: #quick mode
                    BDdemo_new_quick.update({future_:{websites_names:param_websites}})
                else: #sequential mode
                    param_websites["request_future"] = future_
            except Exception:
                continue

# Add future to nested dict with all other results.
        dic_snoop_full[websites_names] = results_site


# Print invalid_data.
    if bool(lst_invalid) is True:
        print("".join(lst_invalid))


## Progress_description.
    if not verbose:
        refresh = False
        refresh_per_second = 4.0 if "demo" in VERSION else (2.0 if not WINDOWS else 1.0)
        if not WINDOWS:
            spin_emoj = 'arrow3' if norm else random.choice(["dots", "dots12"])
            progress = Progress(TimeElapsedColumn(), SpinnerColumn(spinner_name=spin_emoj),
                                "[progress.percentage]{task.percentage:>1.0f}%", BarColumn(bar_width=None, complete_style='cyan',
                                finished_style='cyan bold'), refresh_per_second=refresh_per_second)
        else:
            progress = Progress(TimeElapsedColumn(), "[progress.percentage]{task.percentage:>1.0f}%", BarColumn(bar_width=None,
                                complete_style='cyan', finished_style='cyan bold'), refresh_per_second=refresh_per_second)
    else:
        refresh = True
        progress = Progress(TimeElapsedColumn(), "[progress.percentage]{task.percentage:>1.0f}%", auto_refresh=False)

## Verbalization panel.
        if not ANDROID:
            if color:
                console.print(Panel("[yellow]time[/yellow] | [magenta]exec.[/magenta] | [bold cyan]response (t=s)[/bold cyan] " + \
                                    "| [bold red]tot.[bold cyan]time (T=s)[/bold cyan][/bold red] | " + \
                                    "[bold cyan]data size[/bold cyan] | [bold cyan]avail.memory[/bold cyan]",
                                    title="[cyan]Designation[/cyan]", style=STL(color="cyan")))
            else:
                console.print(Panel("site response (t=s) | total time (T=s) | data size | avail.memory", title="Designation"))
        else:
            if color:
                console.print(Panel("[yellow]time[/yellow] | [magenta]perc.[/magenta] | [bold cyan]response (t=s)[/bold cyan] " + \
                                    "| [bold red]total [bold cyan]time (T=s)[/bold cyan][/bold red] | [bold cyan]data [/bold cyan]" + \
                                    "| [bold cyan]avail.ram[/bold cyan]",
                                    title="[cyan]Designation[/cyan]", style=STL(color="cyan")))
            else:
                console.print(Panel("time | perc. | response (t=s) | total time (T=s) | data | avail.ram", title="Designation"))


## Iterate through future array and get results.
    li_time = [0]
    with progress:
        if color is True:
            task0 = progress.add_task("", total=len(BDdemo_new_quick)) if norm else progress.add_task("", total=len(BDdemo_new))
        iterator_future = iter(as_completed(BDdemo_new_quick)) if norm else iter(BDdemo_new.items())
        for idx, future in enumerate(iterator_future, 1):
            if norm:
                websites_names = [*BDdemo_new_quick.get(future).keys()][0]
                param_websites = [*BDdemo_new_quick.get(future).values()][0]
            else:
                websites_names = future[0]
                param_websites = future[1]
            if color is True:
                progress.update(task0, advance=1, refresh=refresh) #progress.refresh()
# Skip prohibited nickname or skip site from gray-list.
            if dic_snoop_full.get(websites_names).get("exists") is not None:
                continue
# Get site meta information again.
            url = dic_snoop_full.get(websites_names).get("url_user")
            country_emojis = dic_snoop_full.get(websites_names).get("flagcountry")
            country_code = dic_snoop_full.get(websites_names).get("flagcountryklas")
            country_Emoj_Code = country_emojis if not WINDOWS else country_code
# Get expected data type of 4 methods.
            error_type = param_websites["errorType"]
# Response result from server.
            request_future = future if norm else param_websites["request_future"]

            if verbose is True:
                prefix = f"#{idx}::::::::::" if idx else ""
                if color is True:
                    print(f"{prefix}initiate connection to: {Fore.CYAN}{url}{Style.RESET_ALL}\n{prefix}Connecting...")
                else:
                    print(f"{prefix}initiate connection to: {url}\n{prefix}Connecting...")

            r, error_type, response_time = r_results(request_future=request_future, norm=norm,
                                                     error_type=error_type, websites_names=websites_names,
                                                     print_found_only=print_found_only, verbose=verbose,
                                                     color=color, timeout=timeout, country_code=f" ~{country_code}", idx=idx)

# Retry request for failed connection is more effective than through Adapter.
            if norm is False and r == "FakeNone":
                head_duble = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                              'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                              'Sec-Fetch-Mode': 'navigate',
                              'Sec-Fetch-Site': 'none',
                              'Sec-Fetch-User':'?1',
                              'Sec-GPC': '1',
                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                                            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}

                for num, _ in enumerate(range(2), 1):
                    dic_binding["censors"] -= 1
                    if num > 1:
                        head_duble = ""
                    r_retry = executor_req_retry.submit(r_session, url=url, headers=head_duble,
                                                        allow_redirects=allow_redirects, timeout=4)
                    if color is True and print_found_only is False:
                        print(f"{Style.RESET_ALL}{Fore.CYAN}[{Style.BRIGHT}{Fore.RED}-{Style.RESET_ALL}{Fore.CYAN}]" \
                              f"{Style.DIM}{Fore.GREEN} ┌──└──reconnecting{Style.RESET_ALL}")
                    else:
                        if print_found_only is False:
                            print("    ┌──└──reconnecting")

                    r, error_type, response_time = r_results(request_future=r_retry, error_type=param_websites.get("errorType"),
                                                             websites_names=websites_names, print_found_only=print_found_only,
                                                             verbose=verbose, color=color, timeout=4,
                                                             country_code=f" ~{country_code}", idx=idx)

                    if r != "FakeNone":
                        break

                del r_retry

# Collection of faulty bad_zone location.
            if r == None or r == "FakeNone" or r == "FakeStuck":
                dic_binding.get("badzone").append(country_code)
## Check, 4 methods; #1.
# Encoding autodetect for outdated specific lib requests/ISO-8859-1, or manual override via DB.
            try:
                if r is not None and r != "FakeNone" and r != "FakeStuck":
                    if r.content and r.encoding == 'ISO-8859-1': #trap (if r is not None ≠ if r)
                        r.encoding = char_detect(r.content).get("encoding")
                        if r.encoding is None: r.encoding = "utf-8"
                    elif r.content and r.encoding != 'ISO-8859-1' and r.encoding.lower() != 'utf-8':
                        if r.encoding == "cp-1251": r.encoding = "cp1251"
                        elif r.encoding == "cp-1252": r.encoding = "cp1252"
                        elif r.encoding == "windows1251": r.encoding = "windows-1251"
                        elif r.encoding == "windows1252": r.encoding = "windows-1252"
            except Exception:
                r.encoding = "utf-8"

# Responses message (different locations).
            if error_type == "message":
                try:
                    if param_websites.get("encoding") is not None:
                        r.encoding = param_websites.get("encoding")
                except Exception:
                    console.log(snoopbanner.err_all(err_="high"))
                error = param_websites.get("errorMsg")
                error2 = param_websites.get("errorMsg2")
                error3 = param_websites.get("errorMsg3") if param_websites.get("errorMsg3") is not None else "FakeNoneNoneNone"
                if param_websites.get("errorMsg2"):
                    continue

                try:
                    if r.status_code > 200 and param_websites.get("ignore_status_code") is None \
                                                                 or error in r.text or error2 in r.text or error3 in r.text:
                        if not print_found_only and not norm:
                            print_not_found(websites_names, verbose, color, idx)
                        exists = "alas"
                    else:
                        if not norm:
                            print_found_country(websites_names, url, country_Emoj_Code, verbose, color, idx)
                        exists = "found!"
                        if reports:
                            executor_req_save.submit(sreports, url, headers, error_type, username, websites_names, r)
                except UnicodeEncodeError:
                    exists = "alas"
## Check, 4 methods; #2.
# Check username by status 301 and 303 (redirection and salt).
            elif error_type == "redirection":
                if r.status_code == 301 or r.status_code == 303:
                    if not norm:
                        print_found_country(websites_names, url, country_Emoj_Code, verbose, color, idx)
                    exists = "found!"
                    if reports:
                        session_size = executor_req_save.submit(sreports, url, headers, error_type, username, websites_names, r)
                else:
                    if not print_found_only and not norm:
                        print_not_found(websites_names, verbose, color, idx)
                        session_size = len(str(r.content))
                    exists = "alas"
## Check, 4 methods; #3.
# Checks if the response status code is 2..
            elif error_type == "status_code":
                if not r.status_code >= 300 or r.status_code < 200:
                    if not norm:
                        print_found_country(websites_names, url, country_Emoj_Code, verbose, color, idx)
                    if reports:
                        executor_req_save.submit(sreports, url, headers, error_type, username, websites_names, r)
                    exists = "found!"
                else:
                    if not print_found_only and not norm:
                        print_not_found(websites_names, verbose, color, idx)
                    exists = "alas"
## Check, 4 methods; #4.
# Redirection.
            elif error_type == "response_url":
                if 200 <= r.status_code < 300:
                    if not norm:
                        print_found_country(websites_names, url, country_Emoj_Code, verbose, color, idx)
                    if reports:
                        executor_req_save.submit(sreports, url, headers, error_type, username, websites_names, r)
                    exists = "found!"
                else:
                    if not print_found_only and not norm:
                        print_not_found(websites_names, verbose, color, idx)
                    exists = "alas"
## If all 4 methods did not work out, e.g. because of access error (red) or unknown error.
            else:
                exists = "block"

## Attempt to get info from request, write to csv.
            try:
                http_status = r.status_code
            except Exception:
                http_status = "fail" if r != "FakeStuck" else "stuck"

            try: #session in kB
                if reports is True:
                    session_size = session_size if error_type == 'redirection' else len(str(r.content))
                else:
                    session_size = len(str(r.content))

                if session_size >= 555:
                    session_size = round(session_size / 1024)
                elif session_size < 555:
                    session_size = round((session_size / 1024), 2)
            except Exception:
                session_size = "Err"

## Count sites response timings with acceptable preciseness.
# Reaction.
            ello_time = round(float(time.time() - TIME_START), 2) #current
            li_time.append(ello_time)
            dif_time = round(li_time[-1] - li_time[-2], 2) #difference

## Option '-v'.
            if verbose is True:
                if exists == "found!":
                    conn_status = "Username found!"
                elif exists == "alas":
                    conn_status = "Username Not Found!"
                elif exists == "block":
                    conn_status = "Connection Error/Blocked!"
                elif exists == "gray_list":
                    conn_status = "Skipped (Gray List)"
                elif exists == "invalid_nick":
                    conn_status = "Invalid Nickname"
                else:
                    conn_status = "Timeout!"

                if color is True:
                    print(f"{prefix}{Fore.GREEN if exists == 'found!' else Fore.RED if exists == 'alas' else Fore.YELLOW}{conn_status}{Style.RESET_ALL}")
                else:
                    print(f"{prefix}{conn_status}")

                ram_free = mem_test()
                ram_free_color = "[cyan]" if ram_free > 100 else "[red]"
                R = "[red]" if dif_time > 2.7 and dif_time != ello_time else "[cyan]" #delay in total time, color
                R1 = "bold red" if dif_time > 2.7 and dif_time != ello_time else "bold blue"

                if session_size == 0 or session_size is None:
                    Ssession_size = "Head"
                elif session_size == "Err":
                    Ssession_size = "No"
                else:
                    Ssession_size = str(session_size) + " Kb"

                if color is True:
                    console.print(f"[cyan] [*{response_time} s] {R}[*{ello_time} s] [cyan][*{Ssession_size}]",
                                  f"{ram_free_color}[*{ram_free} MB]")
                    console.rule("", style=R1)
                else:
                    console.print(f" [*{response_time} s T] >>", f"[*{ello_time} s t]", f"[*{Ssession_size}]",
                                  f"[*{ram_free} MB]", highlight=False)
                    console.rule(style="color")

## Utility info/CSV, update dictionary with final results.
            if dif_time > 2.7 and dif_time != ello_time:
                dic_snoop_full.get(websites_names)['response_time_site_ms'] = str(dif_time)
            else:
                dic_snoop_full.get(websites_names)['response_time_site_ms'] = "no"
            dic_snoop_full.get(websites_names)['exists'] = exists
            dic_snoop_full.get(websites_names)['session_size'] = session_size
            dic_snoop_full.get(websites_names)['countryCSV'] = country_code
            dic_snoop_full.get(websites_names)['http_status'] = http_status
            dic_snoop_full.get(websites_names)['check_time_ms'] = response_time
            dic_snoop_full.get(websites_names)['response_time_ms'] = str(ello_time)
# Adding the results of this site to the final dictionary along with all other results.
            dic_snoop_full[websites_names] = dic_snoop_full.get(websites_names)
# don't hold server connection resources; prevent memory leak: del future.
            if r != "FakeStuck":
                if norm:
                    BDdemo_new_quick.pop(future, None)
                else:
                    param_websites.pop("request_future", None)

# Release minor part of resources.
        try:
            if 'executor_req_retry' in locals(): executor_req_retry.shutdown()
            if 'executor_req_save' in locals(): executor_req_save.shutdown()
            try:
                if len(lst_username) != 1:
                    executor_req.shutdown()
            except Exception:
                pass
        except Exception:
            console.log(snoopbanner.err_all(err_="low"))
# Return dictionary with all data requested by snoop function and forward held resources (later, close in background).
        return dic_snoop_full, executor_req, nick


## Option '-t'.
def set_timeout(value):
    try:
        timeout = int(value)
    except Exception:
        raise argparse.ArgumentTypeError(f"\n\033[31;1mTimeout '{value}' Err,\033[0m \033[36m" + \
                                         f"specify time in integer seconds.\n \033[0m")
    if timeout <= 0:
        raise argparse.ArgumentTypeError(f"\n\033[31;1mTimeout '{value}' Err,\033[0m \033[36m" + \
                                         f"specify time > 0 sec.\n \033[0m")
    return timeout


## Option '-p'.
def speed_snoop(speed):
    try:
        speed = int(speed)
        if WINDOWS and (speed <= 0 or speed > 150):
            raise Exception("")
        elif speed <= 0 or speed > 300:
            raise Exception("")
        return speed
    except Exception:
        if not WINDOWS:
            raise argparse.ArgumentTypeError(f"\n\033[31;1mMax. workers proc = '{speed}' Err,\033[0m" + \
                                              " \033[36m working range from '1' to '300' as integer.\n \033[0m")
        else:
            snoopbanner.logo(text=format_txt(f" ! Set concurrency is too high: '{speed} threads' makes no sense, " + \
                                             f"reduce the '--pool/-p <= 150' value. Note that, for instance, " + \
                                             f"OS GNU/Linux uses a different technology that makes sense to boost.",
                                             k=True, m=True) + "\n\n", exit=False)
            sys.exit()


## Snoop Project source Code update.
def update_snoop():
    print("""
\033[36mDo you really want to:
                    __             _  
   ._  _| _._|_ _  (_ ._  _  _ ._   ) 
|_||_)(_|(_| |_(/_ __)| |(_)(_)|_) o  
   |                           |    \033[0m""")

    while True:
        print("\033[36mSelect action:\033[0m [y/n] ", end='')
        upd = input().lower()
        if upd == "y":
            print("\033[36mNote: Snoop update function works using the < Git > utility\033[0m")
            subprocess.run("update.bat", shell=True) if WINDOWS else os.system("./update.sh")
            break
        elif upd == "n":
            print(Style.BRIGHT + Fore.RED + "\nUpdate rejected\nExit")
            break
        else:
            print(Style.BRIGHT + Fore.RED + format_txt("{0}└──False, [Y/N] ?", k=True, m=True).format(' ' * 25))
    sys.exit()


## Delete reports.
def autoclean():
    print("""
\033[36mDo you really want to:\033[0m \033[31;1m
               _                _  
 _| _ |  _.|| |_) _ ._  _ .-_|_  ) 
(_|(/_| (_||| | \\(/_|_)(_)|  |_ o  
                    |             \033[0m""")

    while True:
        print("\033[36mSelect action:\033[0m [y/n] ", end='')
        del_all = input().lower()
        if del_all == "y":
            try:
                total_size = 0
                delfiles = []
                for total_file in glob.iglob(os.path.join(DIRPATH, "results") + '/**/*', recursive=True):
                    total_size += os.path.getsize(total_file)
                    if os.path.isfile(total_file): delfiles.append(total_file)

                rm = os.path.join(DIRPATH, "results") if 'source' in VERSION and not ANDROID else DIRPATH
                shutil.rmtree(rm, ignore_errors=True)

                print(f"\n\033[31;1mdeleted --> '{rm}'\033[0m\033[36m {len(delfiles)} files, " + \
                      f"{round(total_size/1024/1024, 2)} MB\033[0m")
            except Exception:
                console.log("[red]Error")
            break
        elif del_all == "n":
            print(Style.BRIGHT + Fore.RED + "\nAction cancelled\nExit")
            break
        else:
            print(Style.BRIGHT + Fore.RED + format_txt("{0}└──False, [Y/N] ?", k=True, m=True).format(' ' * 25))
    sys.exit()


## License/system info.
def license_snoop():
    with open('COPYRIGHT', 'r', encoding="utf8") as copyright:
        wl = 5 if WINDOWS and int(platform.win32_ver()[0]) < 10 else 4
        try:
            ts = os.get_terminal_size()[0]
        except OSError:
            ts = 80
        cop = copyright.read().replace('=' * 80, "~" * (ts - wl)).strip()
        console.print(Panel(cop, title='[bold white]COPYRIGHT[/bold white]',
                            style=STL(color="white", bgcolor="blue"),
                            border_style=STL(color="white", bgcolor="blue")))

    if not ANDROID:
        cpu = 2 if psutil.cpu_count(logical=False) == None else psutil.cpu_count(logical=False)
        pool_ = str(cpu * 7 if WINDOWS else (os.cpu_count() * 40)) + \
                f" {'threads (~600_MB_Ram = 50_Threads = 5_Mbit/s)' if WINDOWS else 'process (~1.2_GB_Ram = 100_Process = 10_Mbit/s)'}"

        if WINDOWS and 'full' in VERSION:
            ram_av = 800
        elif WINDOWS and 'demo' in VERSION:
            ram_av = 500

        if LINUX and 'full' in VERSION:
            ram_av = 3000 if os.cpu_count() > 4 else 700
        elif LINUX and 'demo' in VERSION:
            ram_av = 200

        try:
            ram = int(psutil.virtual_memory().total / 1024 / 1024)
            ram_free = int(psutil.virtual_memory().available / 1024 / 1024)
            if ram_free < ram_av:
                ram_free = f"[bold red]{ram_free}[/bold red]"
            else:
                ram_free = f"[dim cyan]{ram_free}[/dim cyan]"
            os_ver = platform.platform(aliased=True, terse=0)
            threadS = f"thread(s) per core: [dim cyan]{int(psutil.cpu_count() / psutil.cpu_count(logical=False))}[/dim cyan]"
        except Exception:
            console.print(f"\n[bold red]The Snoop version you use: '{VERSION}' is developed for the Android platform, " + \
                          f"but it seems like something else is used 💻\n\nExit")
            sys.exit()
    elif ANDROID:
        pool_ = str(os.cpu_count() * 3) + f" process, (~300_MB_Ram = 25_Process = 4_Mbit/s)"

        try:
            ram = subprocess.check_output("free -m", shell=True, text=True).splitlines()[1].split()[1]
            ram_free = int(subprocess.check_output("free -m", shell=True, text=True).splitlines()[1].split()[-1])
            if ram_free <= 200:
                ram_free = f"[bold red]{ram_free}[/bold red]"
            else:
                ram_free = f"[dim cyan]{ram_free}[/dim cyan]"
            os_ver = 'Android ' + subprocess.check_output("getprop ro.build.version.release", shell=True, text=True).strip()
            threadS = f'model: [dim cyan]{subprocess.check_output("getprop ro.product.cpu.abi", shell=True, text=True).strip()}' + \
                      f'[/dim cyan]'
            T_v = dict(os.environ).get("TERMUX_VERSION")
        except Exception:
            T_v, ram_free, os_ver, threadS = "Not Termux?!", "?", "?", "?"
            ram = "please 'pkg install procps' ... |"

    termux = f"\nTermux: [dim cyan]{T_v}[/dim cyan]\n" if ANDROID else "\n"

    light_v = True if not 'snoopplugins' in globals() else False
    if PYTHON_3_8_PLUS:
        colorama_v = f", (colorama::{version_lib('colorama')})"
        rich_v = f", (rich::{version_lib('rich')})"
        urllib3_v = f", (urllib3::{version_lib('urllib3')})"
        psutil_v = f", (psutil::{version_lib('psutil')})"
        char_v = f", (charset_normalizer::{version_lib('charset_normalizer')})"
    else:
        urllib3_v = f", (urllib3::{requests.urllib3.__version__})"
        colorama_v = ""
        rich_v = ""
        psutil_v = f", (psutil::{psutil.__version__})"
        char_v = ""

    console.print('\n', Panel(f"Program: [blue bold]{'light ' if light_v else ''}[/blue bold][dim cyan]{VERSION}" + \
                                       f"{str(platform.architecture(executable=sys.executable, bits='', linkage=''))}[/dim cyan]\n" + \
                              f"OS: [dim cyan]{os_ver}[/dim cyan]" + termux + \
                              f"Locale: [dim cyan]{locale.setlocale(locale.LC_ALL)}[/dim cyan]\n" + \
                              f"Python: [dim cyan]{platform.python_version()}[/dim cyan]\n" + \
                              f"Key libraries: [dim cyan](requests::{requests.__version__}), (certifi::{certifi.__version__}), " + \
                                             f"(speedtest::{snoopnetworktest.speedtest.__version__}){rich_v}{psutil_v}" + \
                                             f"{colorama_v}{urllib3_v}{char_v}[/dim cyan]\n" + \
                              f"CPU(s): [dim cyan]{os.cpu_count()},[/dim cyan] {threadS}\n" + \
                              f"Ram: [dim cyan]{ram} MB,[/dim cyan] available: {ram_free} [dim cyan]MB[/dim cyan]\n" + \
                              f"Recommended pool: [dim cyan]{pool_}[/dim cyan]",
                              title='[bold cyan]snoop info[/bold cyan]', style=STL(color="cyan")))
    sys.exit()


## MAIN.
def main_cli():
    if not WINDOWS and not MACOS:
        set_start_method('fork')
    if "full" in VERSION:
        premium()
    web_path_copy()
    date_off = license()
    try:
        BDdemo = snoopbanner.DB('BDfull')
    except Exception:
        try:
            BDdemo = snoopbanner.DB('BDdemo')
        except Exception:
            print(Style.BRIGHT + Fore.RED + "Oops, something went wrong..." + Style.RESET_ALL)
            sys.exit()

    try:
        BDflag = snoopbanner.DB('BDflag')
    except Exception:
        BDflag = {}

    flagBS = len(BDdemo)
    web_sites = f"{len(BDflag) // 100}00+"


# Assigning Snoop Project options.
    class SnoopArgumentParser(argparse.ArgumentParser):
        def __init__(self, *args, color=None, **kwargs): #'color' by default appeared in python3.14+, don't raise error in python < 3.14.
            if color is not None:
                try:
                    argparse.ArgumentParser(color=color)
                    kwargs['color'] = color
                except Exception:
                    pass
            super().__init__(*args, **kwargs)

        def print_help(self, out_help = sys.stdout): #remove "--help" from help.
            del_str_help = self.format_help()
            del_str_help = re.sub(r'-h, --help.*\n|this.*|mess.*\n|opti.*\n|and.*\n|sho.*|exit.*', '', del_str_help)
            out_help.write(del_str_help)


    parser = SnoopArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, color=False,
                                 usage="python3 snoop.py [search arguments...] nickname\nor\n" + \
                                       "usage: python3 snoop.py [service arguments | plugins arguments]\n",
                                 epilog=(f"{Fore.CYAN}Snoop {Style.BRIGHT}{Fore.RED}demo version {Style.RESET_ALL}" + \
                                         f"{Fore.CYAN}support: \033[31;1m{flagBS}\033[0m \033[36mWebsites!\n{Fore.CYAN}" + \
                                         f"Snoop \033[36;1mfull version\033[0m \033[36msupport: " + \
                                         f"\033[36;1m{web_sites} \033[0m\033[36mWebsites!!!\033[0m\n\n"))
# Service arguments.
    service_group = parser.add_argument_group('\033[36mservice arguments\033[0m')
    service_group.add_argument("--version", "-V", action="store_true",
                               help="\033[36mA\033[0mbout: print software version, snoop info and License.")
    service_group.add_argument("--list-all", "-l", action="store_true", dest="listing",
                               help="\033[36mP\033[0mrint detailed information about the Snoop database.")
    service_group.add_argument("--donate", "-d", action="store_true", dest="donation",
                               help="\033[36mD\033[0monate to Snoop Project development, get/buy \
                                     \033[32;1mSnoop full version\033[0m.")
    service_group.add_argument("--autoclean", "-a", action="store_true", dest="autoclean", default=False,
                               help="\033[36mD\033[0melete all reports, clear cache.")
    service_group.add_argument("--update", "-U", action="store_true", dest="update",
                               help="\033[36mU\033[0mpdate Snoop.")
# Plugins arguments.
    plugins_group = parser.add_argument_group('\033[36mplugins arguments\033[0m')
    plugins_group.add_argument("--module", action="store_true", dest="module", default=False,
                               help="\033[36mO\033[0mSINT search: enable various Snoop plugins:: IP/GEO/YANDEX.")
# Search arguments.
    search_group = parser.add_argument_group('\033[36msearch arguments\033[0m')
    search_group.add_argument("username", nargs='*', metavar='nickname', action="store", default=None,
                              help="\033[36mN\033[0mickname of the sought user. \
                                    Searching for multiple names simultaneously is supported.\
                                    A nickname containing a space must be enclosed in quotes.")
    search_group.add_argument("--base", "-b <file>", dest="json_file", default="BDdemo", metavar='',
                              help=argparse.SUPPRESS if "demo" in VERSION else "\033[36mS\033[0mpecify a different DB \
                                                                                for 'nickname' search (Local).")
    search_group.add_argument("--web-base", "-w", action="store_true", dest="web", default=False,
                              help=f"\033[36mC\033[0monnect to dynamically updated web_DB for 'nickname' search \
                                    ({web_sites} sites).")
    search_group.add_argument("--site", "-s <site_name>", action="append", metavar='', dest="site_list", default=None,
                              help="\033[36mS\033[0mpecify a site name from '--list-all' DB. Search 'nickname' on one specified resource, \
                                    it is allowed to use the '-s' option multiple times.")
    search_group.add_argument("--exclude", "-e <country_code>", action="append", metavar='', dest="exclude_country", default=None,
                              help="\033[36mE\033[0mxclude the selected region from the search, it is allowed to use the '-e' option \
                                    multiple times, for example, '-e RU -e WR' excludes Russia and the World from the search.")
    search_group.add_argument("--include", "-i <country_code>", action="append", metavar='', dest="one_level", default=None,
                              help="\033[36mI\033[0mnclude only the selected region in the search, \
                                    it is allowed to use the '-i' option multiple times, for example, '-i US -i UA' search in US and Ukraine.")
    search_group.add_argument("--time-out", "-t <digit>", action="store", metavar='', dest="timeout", type=set_timeout, default=8.9,
                              help="\033[36mS\033[0met max response wait time from the server (seconds).\n"
                                   "Affects search duration and 'timeout errors' (default is 9 sec).")
    search_group.add_argument("--country-sort", "-c", action="store_true", dest="country", default=False,
                              help="\033[36mP\033[0mRINT and save results sorted by country, not alphabetically.")
    search_group.add_argument("--no-func", "-n", action="store_true", dest="no_func", default=False,
                              help="\033[36m✓\033[0mMonochrome terminal, no colors in url \
                                    ✓Disable opening web browser\
                                    ✓Disable printing country flags\
                                    ✓Disable progress status and indication.")
    search_group.add_argument("--found-print", "-f", action="store_true", dest="print_found_only", default=False,
                              help="\033[36mP\033[0mrint only found accounts.")
    search_group.add_argument("--verbose", "-v", action="store_true", dest="verbose", default=False,
                              help="\033[36mP\033[0mrint detailed verbalization during 'nickname' search.")
    search_group.add_argument("--multithread", "-m", action="store_true", dest="multithread", default=False,
                              help="\033[36mU\033[0mse multithreading instead of multiprocessing.")
    search_group.add_argument("--userlist", "-u <file>", metavar='', action="store", dest="user", default=False,
                              help="\033[36mS\033[0mpecify a file with a list of users. Snoop will intelligently process \
                                    the data and provide additional reports.")
    search_group.add_argument("--save-page", "-S", action="store_true", dest="reports", default=False,
                              help="\033[36mS\033[0mave found user pages into local html files,\
                              slow mode.")
    search_group.add_argument("--cert-on", "-C", default=False, action="store_true", dest="cert",
                              help=argparse.SUPPRESS)
    search_group.add_argument("--headers", "-H <User-Agent>", metavar='', dest="header_custom", nargs=1, default=None,
                              help=argparse.SUPPRESS)
    _val = "60 max. working threads." if WINDOWS else "300 max. processes."
    search_group.add_argument("--pool", "-p <digit>", metavar='', dest="speed", type=speed_snoop, default=False,
                              help=
                              f"""
                               \033[36mD\033[0misable auto-optimization and manually set search speed from 1 to {_val}
                               By default, high CPU resource utilization is used in Quick mode, in other modes
                               moderate power consumption is used. Too low or high value can significantly
                               slow down the software. ~Estimated optimal value for this device is displayed in 'snoop info',
                               parameter 'Recommended pool', option [--version/-V]. It is suggested to use this option
                               1) if the user has a multi-core PC and plenty of RAM or conversely a weak, rented VPS 
                               2) speeding up/slowing down the search is recommended in tandem with [--found-print/-f] option.
                               """)
    search_group.add_argument("--quick", "-q", action="store_true", dest="norm", default=False,
                              help=
                              """
                              \033[36mF\033[0mast and aggressive search mode.
                              It does not re-process failed resources, as a result the search speeds up,
                              but also slightly increases Bad_raw. Quick mode adapts to PC power,
                              does not print intermediate results,
                              is effective and designed for Snoop full version.
                              """)

    args = parser.parse_args()

## Options '-csei' are mutually exclusive with quick mode.
    if args.norm and 'full' in VERSION:
        print(Fore.CYAN + format_txt("option '-q' enabled: «fast search mode»", k=True))
        args.version, args.listing, args.donation, args.timeout = False, False, False, 8
        args.update, args.module, args.autoclean = False, False, False

        options = []
        options.extend([args.site_list, args.country, args.verbose, args.print_found_only,
                        args.no_func, args.reports, args.cert, args.header_custom, args.speed, args.multithread])

        if any(options) or args.timeout != 8:
            snoopbanner.logo(text=format_txt("⛔️ only options ['-w', '-u', '-e', '-i'] are compatible with quick-mode ['-q']",
                                             k=True, m=True))
    elif args.norm and 'demo' in VERSION:
        snoopbanner.logo("switch '-q' is deactivated in demo: «SNOOPninja/Quick mode»...",
                         color="\033[37m\033[44m", exit=False)
        snoopbanner.donate()
    elif args.norm is False and args.listing is False and args.speed is False and 'full' in VERSION:
        if LINUX:
            print(Fore.CYAN + format_txt("default search '--' enabled: «SNOOPninja mode»", k=True))

    if [args.country, bool(args.site_list), bool(args.exclude_country), bool(args.one_level)].count(True) >= 2:
        snoopbanner.logo(text=format_txt("⛔️ options ['-c', '-e' '-i', '-s'] are mutually exclusive", k=True, m=True))


## Option '-p'.
    if args.speed and 'full' in VERSION:
        thread_proc = "threads" if WINDOWS else "processes"
        print(Fore.CYAN + format_txt(f"option '-p' enabled: «max. working {thread_proc} =" + \
                                     "{0}{1} {2}{3}{4}» {5}".format(Style.BRIGHT, Fore.CYAN, args.speed,
                                                                    Style.RESET_ALL, Fore.CYAN,
                                                                    Style.RESET_ALL), k=True))
    elif args.speed and 'demo' in VERSION:
        snoopbanner.logo("Function '-p' to speed up/slow down the search is available to Snoop full version users...",
                         color="\033[37m\033[44m", exit=False)
        snoopbanner.donate()


## Option '-V' not to be confused with '-v' option.
    if args.version:
        license_snoop()


## Option '-a'.
    if args.autoclean:
        print(Fore.CYAN + format_txt("option '-a' enabled: «delete accumulated reports»", k=True))
        autoclean()


## Option '-H'.
    if args.header_custom:
        print(Fore.CYAN + format_txt("hidden option '-H' enabled: «override user-agent(s)»", k=True), '\n',
              Fore.CYAN + format_txt("User-Agent: '{0}{1}{2}{3}{4}'".format(Style.BRIGHT, Fore.CYAN, ''.join(args.header_custom),
                                                                            Style.RESET_ALL, Fore.CYAN)), sep='')


## Option '-m'.
# Informative output.
    if args.module:
        if not 'snoopplugins' in globals():
            snoopbanner.logo(text=f"\nTHIS IS THE LIGHT VERSION OF SNOOP PROJECT WITH PLUGINS DISABLED\n$ " + \
                                  f"{os.path.basename(sys.argv[0])} --version/-V")
            sys.exit()
        if 'full' in VERSION:
            with console.status("[cyan] checking parameters..."):
                meta(cert=args.cert)

        print(Fore.CYAN + format_txt("option '-m' enabled: «modular search»", k=True))

        def module():
            print(f"\n" + \
                  f"\033[36m╭Choose a plugin or action from the list\033[0m\n" + \
                  f"\033[36m├──\033[0m\033[36;1m[1] --> GEO_IP/domain\033[0m\n" + \
                  f"\033[36m├──\033[0m\033[36;1m[2] --> Reverse Vgeocoder\033[0m\n" + \
                  f"\033[36m├──\033[0m\033[36;1m[3] --> \033[30;1mYandex_parser\033[0m\n" + \
                  f"\033[36m├──\033[0m\033[32;1m[help] --> Help\033[0m\n" + \
                  f"\033[36m└──\033[0m\033[31;1m[q] --> Exit\033[0m\n")

            mod = console.input("[cyan]input --->  [/cyan]")

            if mod == 'help':
                snoopbanner.help_module_1()
                return module()
            elif mod == '1':
                table = Table(title=Style.BRIGHT + Fore.GREEN + "Plugin selected" + Style.RESET_ALL, style="green", header_style='green')
                table.add_column("GEO_IP/domain_v0.6", style="green", justify="center")
                table.add_row('Getting information about ip/domain/url of the target or from a list of this data')
                console.print(table)

                snoopplugins.module1()
            elif mod == '2':
                table = Table(title=Style.BRIGHT + Fore.GREEN + "Plugin selected" + Style.RESET_ALL, style="green", header_style='green')
                table.add_column("Reverse Vgeocoder_v0.6", style="green", justify="center")
                table.add_row('Geographic visualization of coordinates')
                console.print(table)

                snoopplugins.module2()
            elif mod == '3':
                table = Table(title=Style.BRIGHT + Fore.GREEN + "Plugin selected" + Style.RESET_ALL, style="green", header_style='green')
                table.add_column("Yandex_parser_v0.5", style="green", justify="center")
                table.add_row('Yandex parser: Ya_Reviews; Ya_Q; Ya_Market; Ya_Music; Ya_Zen; Ya_Disk; E-mail; Name.')
                console.print(table)

                snoopplugins.module3()
            elif mod == 'q':
                print(Style.BRIGHT + Fore.RED + "└──Exit")
                sys.exit()
            else:
                print(Style.BRIGHT + Fore.RED + "└──Invalid choice\n" + Style.RESET_ALL)
                return module()

        module()
        sys.exit()


## Options '-f' + "-v".
    if args.verbose is True and args.print_found_only is True:
        snoopbanner.logo(text=format_txt("⛔️ detailed verbalization mode [option '-v'] displays detailed information, " + \
                                         "[option '-f'] is inappropriate", k=True, m=True))


## Option '-C'.
    if args.cert:
        print(Fore.CYAN + format_txt("hidden option '-C' enabled: «check certificates on servers on»", k=True))


## Option '-w'.
    if args.web:
        print(Fore.CYAN + format_txt("option '-w' enabled: «connect to external web_database»", k=True))


## Option '-S'.
    if args.reports:
        print(Fore.CYAN + format_txt("option '-S' enabled: «save pages of found accounts»", k=True))


## Option '-n'.
    if args.no_func:
        print(Fore.CYAN + format_txt("option '-n' enabled: «disabled:: colors; flags; browser; progress»", k=True))


## Option '-t'.
    if args.timeout != 8.9 and args.norm is False:
        print(Fore.CYAN + format_txt("option '-t' enabled: wait for response from " + \
                                     "site up to{0}{1} {2} {3}{4}sec.» {5}".format(Style.BRIGHT, Fore.CYAN, args.timeout,
                                                                               Style.RESET_ALL, Fore.CYAN,
                                                                               Style.RESET_ALL), k=True))
    if args.timeout == 8.9:
        args.timeout = 9


## Option '-f'.
    if args.print_found_only:
        print(Fore.CYAN + format_txt("option '-f' enabled: «print only found accounts»", k=True))


## Option '-s'.
    if args.site_list:
        print(Fore.CYAN + format_txt(f"option '-s' enabled: «search{Style.BRIGHT}{Fore.CYAN} {', '.join(args.username)}" + \
                                     f"{Style.RESET_ALL} {Fore.CYAN}on selected website(s)»", k=True), '\n',
              Fore.CYAN + format_txt("it is allowed to use option '-s' multiple times"), "\n",
              Fore.CYAN + format_txt("[option '-s'] is mutually exclusive with [options '-с', '-e', '-i']"), sep="")


## Option '--list-all'.
    if args.listing:
        print(Fore.CYAN + format_txt("option '-l' enabled: «detailed info about Snoop DB»", k=True))
        print("\033[36m\nSort Snoop DB by countries, by site name, or aggregated ?\n" + \
              "by countries —\033[0m 1 \033[36mby name —\033[0m 2 \033[36mall —\033[0m 3\n")

# General output of countries (3!).
# Output for full/demo version.
        def sort_list_all(DB, fore, version, line=False):
            listfull = []
            if sortY == "3":
                if line:
                    console.rule("[cyan]Ok, print All Country", style="cyan bold")
                print("")
                li = [DB.get(con).get("country_klas") if WINDOWS else DB.get(con).get("country") for con in DB]
                cnt = str(Counter(li))
                try:
                    flag_str_sum = (cnt.split('{')[1]).replace("'", "").replace("}", "").replace(")", "")
                    all_ = str(len(DB))
                except Exception:
                    flag_str_sum = str("DB corrupted.")
                    all_ = "-1"
                table = Table(title=Style.BRIGHT + fore + version + Style.RESET_ALL, header_style='green', style="green")
                table.add_column("Geolocation: Number of websites", style="magenta", justify='full')
                table.add_column("All", style="cyan", justify='full')
                table.add_row(flag_str_sum, all_)
                console.print(table)

# Sorting alphabetically for full/demo version (2!).
            elif sortY == "2":
                if line:
                    console.rule("[cyan]Ok, sorting alphabetically", style="cyan bold")
                if version == "demo version":
                    console.print('\n', Panel.fit("++Database++", title=version,
                    style=STL(color="cyan", bgcolor="red"), border_style=STL(color="cyan", bgcolor="red")))
                else:
                    console.print('\n', Panel.fit("++Database++", title=version,
                    style=STL(color="cyan"), border_style=STL(color="cyan")))
                i = 0
                sorted_dict_v_listtuple = sorted(DB.items(), key=lambda x: x[0].lower()) #sort dict by main key case-insensitive
                datajson_sort = dict(sorted_dict_v_listtuple) #convert back to dict (sorted)

                for con in datajson_sort:
                    S = datajson_sort.get(con).get("country_klas") if WINDOWS else datajson_sort.get(con).get("country")
                    i += 1
                    listfull.append(f"\033[36;2m{i}.\033[0m \033[36m{S}  {con}")
                print("\n~~~~~~~~~~~~~~~~\n".join(listfull), "\n")

# Sorting by countries for full/demo version (1!).
            elif sortY == "1":
                listwindows = []

                if line:
                    console.rule("[cyan]Ok, sorting by countries", style="cyan bold")

                for con in DB:
                    S = DB.get(con).get("country_klas") if WINDOWS else DB.get(con).get("country")
                    listwindows.append(f"{S}  {con}\n")

                if version == "demo version":
                    console.print('\n', Panel.fit("++Database++", title=version,
                    style=STL(color="cyan", bgcolor="red"), border_style=STL(color="cyan", bgcolor="red")))
                else:
                    console.print('\n', Panel.fit("++Database++",
                    title=version, style=STL(color="cyan"), border_style=STL(color="cyan")))

                for i in enumerate(sorted(listwindows, key=str.lower), 1):
                    listfull.append(f"\033[36;2m{i[0]}. \033[0m\033[36m{i[1]}")
                print("~~~~~~~~~~~~~~~~\n".join(listfull))

# Running '--list-all' function.
        while True:
            sortY = console.input("[cyan]Select action: [/cyan]")
            if sortY == "1" or sortY == "2":
                sort_list_all(BDflag, Fore.GREEN, "full version", line=True)
                sort_list_all(BDdemo, Fore.RED, "demo version")
                break
            elif sortY == "3":
                sort_list_all(BDdemo, Fore.RED, "demo version", line=True)
                sort_list_all(BDflag, Fore.GREEN, "full version")
                break
# No action selected '--list-all'.
            else:
                print(Style.BRIGHT + Fore.RED + format_txt("{0}└──False, [1/2/3] ?", k=True, m=True).format(' ' * 19))
        sys.exit()


## Donation option '-d'.
    if args.donation:
        print(Fore.CYAN + format_txt("option '-d' enabled: «financial support for the project»", k=True))
        snoopbanner.donate()


## Option '-u' specifiing a file-list of searched users.
    user_list = []
    if args.user:
        userlists, userlists_bad, duble, _duble, short_user = [], [], [], [], []
        flipped, d = {}, {}

        try:
            patchuserlist = ("{}".format(args.user))
            userfile = os.path.basename(patchuserlist)
            print(Fore.CYAN + format_txt("option '-u' enabled: «searching for nickname(s) from file:: {0}{1}{2}{3}{4}» {5}",
                                         k=True).format(Style.BRIGHT, Fore.CYAN, userfile,
                                                        Style.RESET_ALL, Fore.CYAN, Style.RESET_ALL))

            with open(patchuserlist, "r", encoding="utf8") as u1:
                userlist = [(line[0], line[1].strip()) for line in enumerate(u1.read().replace("\ufeff", "").splitlines(), 1)]

                for num, user in userlist:
                    i_for = (num, user)
                    if check_invalid_username(user, symbol_bad_username=True, phone=True, dot=True, email=True) is False:
                        if all(i_for[1] != x[1] for x in userlists_bad):
                            userlists_bad.append(i_for)
                        else:
                            duble.append(i_for)
                        continue
                    elif user == "":
                        continue
                    elif len(user) <= 2:
                        short_user.append(i_for)
                        continue
                    else:
                        if all(i_for[1] != x[1] for x in userlists):
                            userlists.append(i_for)
                        else:
                            duble.append(i_for)

        except Exception as e:
            print(f"\n\033[31;1mCannot find/read file: '{userfile}'.\033[0m \033[36m\n " + \
                  f"\nPlease, specify a text file with encoding —\033[0m \033[36;1mutf-8.\033[0m\n" + \
                  f"\033[36mBy default, for example, Notepad in Windows OS saves text with encoding — ANSI.\033[0m\n" + \
                  f"\033[36mOpen your file '{userfile}' and change encoding [File ---> Save As ---> utf-8].\n" + \
                  f"\033[36mOr delete unreadable special characters from the file.")
            sys.exit()

        console.rule("[green]Data analysis[/green]")

# good user.
        if userlists:
            _userlists = [f"[dim cyan]{num}.[/dim cyan] {v} [{k}]".replace("", "") for num, (k, v) in enumerate(userlists, 1)]
            console.print(Panel.fit("\n".join(_userlists).replace("%20", " "),
                                    title=f"[cyan]valid ({len(userlists)})[/cyan]", style=STL(color="cyan")))

# duplicate user.
        if duble:
            dict_duble = dict(duble)
            for key, value in dict_duble.items():
                if value not in flipped:
                    flipped[value] = [key]
                else:
                    flipped[value].append(key)

            for k,v in flipped.items():
                k = f"{k} ({len(v)})"
                d[k] = v

            for num, (k, v) in enumerate(d.items(), 1):
                str_1 = f"[dim yellow]{num}.[/dim yellow] {k} {v}".replace(" (", " ——> ").replace(")", " pcs.")
                str_2 = str_1.replace("——> ", "——> [bold yellow]").replace(" pcs.", " pcs.[/bold yellow]")
                _duble.append(str_2)

            print(f"\n\033[36mthe following nickname(s) from '\033[36;1m{userfile}\033[0m\033[36m' contain " + \
                  f"\033[33mduplicates\033[0m\033[36m and will be skipped:\033[0m")
            console.print(Panel.fit("\n".join(_duble), title=f"[yellow]duplicate ({len(duble)})[/yellow]",
                                    style=STL(color="yellow")))

# bad user.
        if userlists_bad:
            _userlists_bad = [f"[dim red]{num}.[/dim red] {v} [{k}]" for num, (k, v) in enumerate(userlists_bad, 1)]
            print(f"\n\033[36mthe following nickname(s) from '\033[36;1m{userfile}\033[0m\033[36m' contain " + \
                  f"\033[31;1mN/A characters\033[0m\033[36m and will be skipped:\033[0m")
            console.print(Panel.fit("\n".join(_userlists_bad),
                                    title=f"[bold red]invalid_data ({len(userlists_bad)})[/bold red]",
                                    style=STL(color="bright_red")))

# Short user.
        if short_user:
            _short_user = [f"[dim red]{num}.[/dim red] {v} [{k}]" for num, (k, v) in enumerate(short_user, 1)]
            print(f"\n\033[36mthe following nickname(s) from '\033[36;1m{userfile}\033[0m\033[36m'\033[0m " + \
                  f"\033[31;1mare shorter than 3 characters\033[0m\033[36m and will be skipped:\033[0m")
            console.print(Panel.fit("\n".join(_short_user).replace("%20", " "),
                                    title=f"[bold red]short nickname ({len(short_user)})[/bold red]",
                                    style=STL(color="bright_red")))

# Save bad_nickname(s) in a separate txt file.
        if short_user or userlists_bad:
            for bad_user1, bad_user2 in itertools.zip_longest(short_user, userlists_bad):
                with open (f"{DIRPATH}/results/nicknames/bad_nicknames.txt", "a", encoding="utf-8") as bad_nick:
                    if bad_user1:
                        bad_nick.write(f"{time.strftime('%Y-%m-%d_%H:%M:%S', TIME_DATE)}  <FILE: {userfile}>  '{bad_user1[1]}'\n")
                    if bad_user2:
                        bad_nick.write(f"{time.strftime('%Y-%m-%d_%H:%M:%S', TIME_DATE)}  <FILE: {userfile}>  '{bad_user2[1]}'\n")


        user_list = [i[1] for i in userlists]

        del userlists, duble, userlists_bad, _duble, short_user, flipped, d

        if bool(user_list) is False:
            print("\n", Style.BRIGHT + Fore.RED + format_txt("⛔️ File '{0}' does not contain any valid nickname".format(userfile),
                                                             k=True, m=True), "\n\n\033[31;1mExit\033[0m\n", sep="")
            sys.exit()


## Checking other (including repeated) options.
## Option '--update' update Snoop.
    if args.update:
        print(Fore.CYAN + format_txt("option '-U' enabled: «snoop update»", k=True))
        update_snoop()


## Option '-w'.
    if args.web:
        # Check if web functionality is actually implemented in plugins or core.
        # Currently the logic seems to be missing in the open source version,
        # but the check blocking it is removed to allow attempts.
        pass


## Option '-b'. Check if an alternative database exists, otherwise default.
    if args.json_file != "BDdemo":
        if not os.path.exists(str(args.json_file)):
            print(f"\n\033[31;1mError! Invalid file path specified: '{str(args.json_file)}'.\033[0m")
            sys.exit()
        else:
            try:
                BDdemo = snoopbanner.DB(args.json_file)
                print(f"{Fore.CYAN}Database loaded from file: {args.json_file}{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n\033[31;1mError loading database '{args.json_file}': {e}\033[0m")
                sys.exit()


## Option '-c'. Sorting by countries.
    sort_web_BDdemo_new = {}
    lap = []
    if args.country is True and args.web is False:
        print(Fore.CYAN + format_txt("option '-c' enabled: «sorting/recording results by countries»", k=True))
        country_sites = sorted(BDdemo, key=lambda k: ("country" not in k, BDdemo[k].get("country", sys.maxsize)))
        for site in country_sites:
            sort_web_BDdemo_new[site] = BDdemo.get(site)


## Function for options '-ei'.
    def one_exl(one_exl_, bool_):
        lap = []
        bd_flag = []

        for k, v in BDdemo.items():
            bd_flag.append(v.get('country_klas').lower())
            if all(item.lower() != v.get('country_klas').lower() for item in one_exl_) is bool_:
                BDdemo_new[k] = v

        enter_coun_u = [x.lower() for x in one_exl_]
        lap = list(set(bd_flag) & set(enter_coun_u))
        diff_list = list(set(enter_coun_u) - set(bd_flag)) #output unique elems from enter_coun_u else set(enter_coun_u)^set(bd_flag)

        if bool(BDdemo_new) is False:
            print('\n', format_txt(f"⛔️ \033[31;1m[{str(diff_list).strip('[]')}] please check input, " + \
                                   f"as all specified search regions are invalid.\033[0m", k=True, m=True), sep='')
            sys.exit()
# Return correct and bad lists of user input in CLI.
        return lap, diff_list


## If options '-sei' are not specified, then use DB as is.
    BDdemo_new = {}
    if args.site_list is None and args.exclude_country is None and args.one_level is None:
        BDdemo_new = BDdemo


## Option '-s'.
    elif args.site_list is not None:
# Make sure that sites are in the database, create a shortened database of site(s) for verification.
        for site in args.site_list:
            for site_yes in BDdemo:
                if site.lower() == site_yes.lower():
                    BDdemo_new[site_yes] = BDdemo[site_yes] #select found sites from DB into dictionary
            try:
                diff_k_bd = set(BDflag) ^ set(BDdemo)
            except Exception:
                snoopbanner.logo(text="\nnickname(s) not specified")
            for site_yes_full_diff in diff_k_bd:
                if site.lower() == site_yes_full_diff.lower(): #if site (-s) is in Full version DB
                    print(format_txt("{0}⛔️ skip:{2} {3}site from DB {4}full-version{5} {6}is unavailable in{7} " + \
                                     "{8}demo-version{9}{10}:: '{11}{1}{12}{13}'{14}",
                                     k=True, m=True).format(Style.BRIGHT + Fore.RED, site_yes_full_diff,
                                                            Style.RESET_ALL, Fore.CYAN, Style.BRIGHT + Fore.CYAN,
                                                            Style.RESET_ALL, Fore.CYAN, Style.RESET_ALL,
                                                            Style.BRIGHT + Fore.YELLOW, Style.RESET_ALL,
                                                            Fore.CYAN, Style.BRIGHT + Fore.BLACK,
                                                            Style.RESET_ALL, Fore.CYAN, Style.RESET_ALL))

            if not any(site.lower() == site_yes_full.lower() for site_yes_full in BDflag): #if no site match
                print(format_txt("{0}⛔️ skip:{1} {2}desired site is missing in Snoop DB:: '" + \
                                 "{3}{4}{5}' {6}", k=True, m=True).format(Style.BRIGHT + Fore.RED, Style.RESET_ALL, Fore.CYAN,
                                                                          Style.BRIGHT + Fore.RED, site,
                                                                          Style.RESET_ALL + Fore.CYAN, Style.RESET_ALL))
# Cancel search if there is no match in DB for '-s'.
        if not BDdemo_new:
            sys.exit()


## Option '-e'.
# Create shortened site database for checking.
# Create and add sites to new DB whose arguments (-e) != country codes (country_klas).
    elif args.exclude_country is not None:
        lap, diff_list = one_exl(one_exl_=args.exclude_country, bool_=True)
        str_e = "option '-e' enabled: «exclude selected regions from search»::" + \
                                     "{0} {1} {2} {3} {4} {5}".format(Fore.CYAN, str(lap).strip('[]').upper(),
                                                                      Style.RESET_ALL, Style.BRIGHT + Fore.RED,
                                                                      str(diff_list).strip('[]'), Style.RESET_ALL)
        print(Fore.CYAN + format_txt(str_e, k=True), '\n',
              Fore.CYAN + format_txt("it is allowed to use option '-e' multiple times", m=True), '\n',
              Fore.CYAN + format_txt("[option '-e'] is mutually exclusive with [options '-s', '-c', '-i']", m=True), sep='')


## Option '-i'.
# Create shortened site database for checking.
# Create and add sites to new DB whose arguments (-e) != country codes (country_klas).
    elif args.one_level is not None:
        lap, diff_list = one_exl(one_exl_=args.one_level, bool_=False)
        str_i = "option '-i' enabled: «include only selected regions in search»::" + \
                                     "{0} {1} {2} {3} {4} {5}".format(Fore.CYAN, str(lap).strip('[]').upper(),
                                                                      Style.RESET_ALL, Style.BRIGHT + Fore.RED,
                                                                      str(diff_list).strip('[]'), Style.RESET_ALL)
        print(Fore.CYAN + format_txt(str_i, k=True), '\n',
              Fore.CYAN + format_txt("it is allowed to use option '-i' multiple times", m=True), '\n',
              Fore.CYAN + format_txt("[option '-i'] is mutually exclusive with [options '-s', '-c', 'e']", m=True), sep='')


## Nickname not specified or options contradiction.
    if bool(args.username) is False and bool(args.user) is False:
        snoopbanner.logo(text="\nparameters or nickname(s) not specified")
    if bool(args.username) is True and bool(args.user) is True:
        print('\n⛔️' + format_txt("\033[31;1m select nickname(s) from file for search or specify in CLI,\n" + \
              "but not joint use of nickname(s): from file and CLI", k=True, m=True), "\033[31;1m\n\nExit\033[0m")
        sys.exit()


## Option '-v'.
    if args.verbose and bool(args.username) or args.verbose and bool(user_list):
        print(Fore.CYAN + format_txt("option '-v' enabled: «detailed verbalization in CLI»\n", k=True))
        snoopnetworktest.nettest()


## Option '-w' active/inactive.
    try:
        if args.web is False:
            _DB = f"_[_{len(BDdemo_new)}_]" if len(BDdemo_new) != len(BDdemo) else ""
            print(f"\n{Fore.CYAN}local database loaded: {Style.BRIGHT}{Fore.CYAN}{len(BDdemo)}_Websites{_DB}{Style.RESET_ALL}")
    except Exception:
        print("\033[31;1mInvalid loaded database.\033[0m")


## Checking lib versions: 'requests/urllib3'.
    warning_lib()


## Spinning user's.
    def starts(SQ):
# Meta information.
        if 'full' in VERSION:
            meta(cert=args.cert)

# Selecting correct encoding for CSV with respect to OS/geolocation.
        try:
            if "ru" in os.getenv("LANG", ""): #if os.environ.get('LANG') is not None and 'ru' in os.environ.get('LANG'):
                rus_unix = True
            else:
                rus_unix = False
            if WINDOWS and "1251" in locale.setlocale(locale.LC_ALL):
                rus_windows = True
            else:
                rus_windows = False
        except Exception:
            rus_unix = False
            rus_windows = False

        kef_user = 0
        ungzip, ungzip_all, find_url_lst, el = [], [], [], []
        exl = "/".join(lap).upper() if args.exclude_country is not None else "no" #excluded_regions_valid
        one = "/".join(lap).upper() if args.one_level is not None else "no" #included_regions_valid
        for username in SQ:
            kef_user += 1
            sort_sites = sort_web_BDdemo_new if args.country is True else BDdemo_new

            FULL, hardware, nick = snoop(username, sort_sites, country=args.country, user=args.user, verbose=args.verbose,
                                         cert=args.cert, norm=args.norm, reports=args.reports, lst_username=args.username,
                                         print_found_only=args.print_found_only, timeout=args.timeout,
                                         color=not args.no_func, header_custom=args.header_custom, speed=args.speed, multithread=args.multithread)

            exists_counter = 0

            if bool(FULL) is False:
                kef_user -= 1
                cli_file = " <CLI>       " if args.user is False else f" <FILE: {userfile}>"
                with open (f"{DIRPATH}/results/nicknames/bad_nicknames.txt", "a", encoding="utf-8") as bad_nick:
                    bad_nick.write(f"{time.strftime('%Y-%m-%d_%H:%M:%S', TIME_DATE)} {cli_file}  '{username}'\n")

                continue


## Writing to txt report.
            file_txt = open(f"{DIRPATH}/results/nicknames/txt/{username}.txt", "w", encoding="utf-8")

            file_txt.write(f"GEO | RESOURCE {' ' * 16} | URL" + "\n\n")

            for website_name in FULL:
                dictionary = FULL[website_name]
                if type(dictionary.get("session_size")) != str:
                    ungzip.append(dictionary.get("session_size")), ungzip_all.append(dictionary.get("session_size"))
                if dictionary.get("exists") == "found!":
                    exists_counter += 1
                    find_url_lst.append(exists_counter)
                    txt_str = f"{dictionary['flagcountryklas']}  |  {(website_name)}"
                    kef_indent = 30 - (len(txt_str))
                    file_txt.write(f"{txt_str} {' ' * kef_indent} |  {dictionary['url_user']}\n")
# Personal and total session size, except CSV.
            try:
                sess_size = round(sum(ungzip) / 1024, 2) #in MB
                s_size_all = round(sum(ungzip_all) / 1024, 2) #in MB
            except Exception:
                sess_size = 0.000_000_000_1
                s_size_all = "Err"

            timefinish = time.time() - TIME_START - sum(el)
            el.append(timefinish)
            time_all = str(round(time.time() - TIME_START))
            

            file_txt.write("\n" f"Requested object: <{nick}> found: {exists_counter} time(s).")
            file_txt.write("\n" f"Session: {str(round(timefinish))}sec {str(sess_size)}MB.")
            file_txt.write("\n" f"Snoop Database (demo version): {flagBS} Websites.")
            file_txt.write("\n" f"Excluded regions: {exl}.")
            file_txt.write("\n" f"Selection of specific regions: {one}.")
            file_txt.write("\n" f"Updated: {time.strftime('%Y-%m-%d_%H:%M:%S', TIME_DATE)}.\n")
            file_txt.write("\n" f"©2020-{time.localtime().tm_year} «Snoop Project» (demo version).")
            file_txt.close()


## Writing to html report.
            if ANDROID and re.search("[^\\W \\da-zA-Z]+", nick):
                username = f"nickname_{time.strftime('%Y-%m-%d_%H-%M-%S')}"

            file_html = open(f"{DIRPATH}/results/nicknames/html/{username}.html", "w", encoding="utf-8")

            path_ = DIRPATH if not ANDROID else "/storage/emulated/0/snoop"
            file_html.write("<!DOCTYPE html>\n<html lang='en'>\n\n<head>\n<title>◕ Snoop HTML report</title>\n" + \
                            "<meta charset='utf-8'>\n<style>\nbody {background: url(../../../web/public.png) " + \
                            "no-repeat 20% 0%}\n.str1{text-shadow: 0px 0px 20px #333333}\n.shad{display: inline-block}\n" + \
                            ".shad:hover{text-shadow: 0px 0px 14px #6495ED; transform: scale(1.1); transition: transform 0.15s}\n" + \
                            "</style>\n<link rel='stylesheet' href='../../../web/style.css'>\n</head>\n\n<body id='snoop'>\n\n" + \
                            "<div id='particles-js'></div>\n\n" + \
                            "<h1><a class='GL' href='file://" + f"{path_}/results/nicknames/html/'>open file</a>" + "</h1>\n")
            file_html.write("<h3>Snoop Project (demo version)</h3>\n<p>Click: 'sort by countries', return:" + \
                            "'<span style='text-shadow: 0px 0px 13px #40E0D0'>F5'</span></p>\n<div id='report'>\n" + \
                            "<button onclick='sortList()'>Sort by countries ↓↑</button><br>\n<ol" + " id='id777'>\n")

            li = []
            for website_name in FULL:
                dictionary = FULL[website_name]
                flag_sum = dictionary["flagcountry"]
                if dictionary.get("exists") == "found!":
                    li.append(flag_sum)
                    file_html.write("<li><span class='shad'>" + dictionary["flagcountry"] + \
                                    "<a target='_blank' href='" + dictionary["url_user"] + "'>" + \
                                    (website_name) + "</a></span></li>\n")
            try:
                cnt = []
                for k, v in sorted(Counter(li).items(), key=lambda x: x[1], reverse=True):
                    cnt.append(f"【{k} ⇔ {v}】")
                flag_str_sum = "; ".join(cnt)
            except Exception:
                flag_str_sum = "-1"

            file_html.write("</ol>\n</div>\n\n<br>\n\n<div id='meta'>GEO:" + flag_str_sum + ".\n")
            file_html.write("<br> Requested object &lt; <b>" + str(nick) + "</b> &gt; found: <b>" + \
                            str(exists_counter) + "</b> time(s).")
            file_html.write("<br> Session: " + "<b>" + str(round(timefinish)) + "sec_" + str(sess_size) + "MB</b>.\n")
            file_html.write("<br> Excluded regions: <b>" + str(exl) + "</b>.\n")
            file_html.write("<br> Selection of specific regions: <b>" + str(one) + "</b>.\n")
            file_html.write("<br> Snoop Database (demo version): <b>" + str(flagBS) + "</b>" + " Websites.\n")
            file_html.write("<br> Updated: " + "<i><b>" + time.strftime("%Y-%m-%d</b>_%H:%M:%S", TIME_DATE) + \
                            ".</i><br><br>\n</div>\n")
            file_html.write("""
<br>

<script>
function sortList() {
    var list = document.getElementById('id777');

    if (!list) {
        console.error("Error: element 'id777' not found.");
        return;
    }

    var items = Array.from(list.getElementsByTagName('LI'));

    if (items.length === 0) {
        return;
    }

    var itemsWithKeys = items.map(function(item) {
        var sortElement = item.querySelector('.shad');
        var sortKey = sortElement ? sortElement.innerText : '';
        return {
            element: item,
            key: sortKey
        };
    });

    itemsWithKeys.sort(function(a, b) {
        return a.key.localeCompare(b.key, 'en', { sensitivity: 'base' });
    });

    var fragment = document.createDocumentFragment();
    itemsWithKeys.forEach(function(itemData) {
        fragment.appendChild(itemData.element);
    });

    list.innerHTML = '';
    list.appendChild(fragment);
}

function rnd(min, max) {
  return Math.random() * (max - min) + min;
}

var don = decodeURIComponent(escape(window.atob("\\
4oyb77iPINCh0L/QsNGB0LjQsdC+INC30LAg0LjQvdGC0LXRgNC10YEg0LogU25vb3AgZGVtbyB2\\
ZXJzaW9uLgoK0JXRgdC70Lgg0LjQvNC10LXRgtGB0Y8g0LLQvtC30LzQvtC20L3QvtGB0YLRjCwg\\
0L/QvtC00LTQtdGA0LbQuNGC0LUg0YTQuNC90LDQvdGB0L7QstC+INGN0YLQvtGCINGD0L3QuNC6\\
0LDQu9GM0L3Ri9C5IElULdC/0YDQvtC10LrRgjoK0L/QvtC70YPRh9C40YLQtSBTbm9vcCBmdWxs\\
IHZlcnNpb24g0LHQtdC3INC+0LPRgNCw0L3QuNGH0LXQvdC40LkuCgpD0LwuICJzbm9vcF9jbGku\\
YmluIC0taGVscCAvIHNub29wX2NsaS5leGUgLS1oZWxwIi4K")))

var don1 = decodeURIComponent(escape(window.atob("\\
PGZvbnQgY29sb3I9InJlZCIgc2l6ZT0iMiI+4oybIFNub29wIGRlbW8gdmVyc2lvbi48L2ZvbnQ+\\
Cjxicj48YnI+CtCU0LvRjyDQv9C+0LTQtNC10YDQttC60Lgg0JHQlCDQuCDQtNCw0LvRjNC90LXQ\\
udGI0LXQs9C+INGA0LDQt9Cy0LjRgtC40Y8g0J/QniDigJQg0L/RgNC+0LXQutGC0YMg0YLRgNC1\\
0LHRg9C10YLRgdGPINGE0LjQvdCw0L3RgdC+0LLQsNGPINC/0L7QtNC00LXRgNC20LrQsC48YnI+\\
CtCf0L7QtNC00LXRgNC20LjRgtC1INGA0LDQt9GA0LDQsdC+0YLRh9C40LrQsCDQuCDQtdCz0L4g\\
0LjRgdGB0LvQtdC00L7QstCw0L3QuNGPINC00L7QvdCw0YLQvtC8LCDQuNC70Lgg0L/RgNC40L7Q\\
sdGA0LXRgtCw0Y8gPGI+PGZvbnQgY29sb3I9ImdyZWVuIj5Tbm9vcCBmdWxsIHZlcnNpb24hPC9m\\
b250PjwvYj4KPGJyPjxicj4KQ9C8LiAic25vb3BfY2xpLmJpbiAtLWhlbHAgLyBzbm9vcF9jbGku\\
ZXhlIC0taGVscCIuCg==")))

func = setInterval(() => {alert(don)}, rnd(30, 45) * 1000)
func1 = setTimeout(() => {id777.onmouseover = function() {document.write(don1)}}, rnd(55, 75) * 1000)
</script>

<script src="../../../web/particles.js"></script>
<script src="../../../web/app.js"></script>

<audio title="Megapolis.mp3 (the year 2020)" controls="controls" autoplay="autoplay">
<source src="../../../web/Megapolis%20(remix).mp3" type="audio/mpeg">
</audio>

<br>

<audio title="for snoop in cyberpunk.mp3 (the year 2020)" controls="controls">
<source src="../../../web/for%20snoop%20in%20cyberpunk.mp3" type="audio/mpeg">
</audio>

<br><br>

<div id='buttons'>
<a target='_blank' href='https://github.com/snooppr/snoop' class="SnA"><span class="SnSpan">🛠  Source Code</span></a>
<a target='_blank' href='https://drive.google.com/file/d/12DzAQMgTcgeG-zJrfDxpUbFjlXcBq5ih/view' \
class="DnA"><span class="DnSpan">📖 Documentation</span></a>
<a onclick='bay()' class="DnA"><span class="DnSpan">💳 Get Full_Version</span></a>
</div>

<br><br>\n
""" + \

snoopbanner.buy() + \

f"""\n\n<p class='str1'><span style="color: gray"><small><small>Report created in Snoop Project software. <br> ©2020-\
{time.localtime().tm_year} «Snoop Project».</small></small></span></p>

<script>
if(typeof don == "undefined" || typeof don1 == "undefined" || don.length != 216 || don1.length != 335 || typeof func == "undefined" \
|| typeof func1 == "undefined")
document.getElementById('snoop').innerHTML=""
</script>

</body>
</html>""")
            file_html.close()


## Writing to csv report.
            file_csv = open(f"{DIRPATH}/results/nicknames/csv/{username}.csv", "w", newline='', encoding="utf-8-sig")

            usernamCSV = re.sub(" ", "_", nick)

            try:
                err_all = dic_binding.get('censors') / kef_user #err_connection_all
                flagBS_err = round(err_all * 100 / (len(BDdemo_new) - len(dic_binding.get("badraw"))), 2)
            except ZeroDivisionError:
                flagBS_err = 0

            try:
                bad_zone = f"~{Counter(dic_binding.get('badzone')).most_common(2)[0][0]}/" + \
                           f"{Counter(dic_binding.get('badzone')).most_common(2)[1][0]}"
            except IndexError:
                try:
                    bad_zone = f"~{Counter(dic_binding.get('badzone')).most_common(2)[0][0]}"
                except IndexError:
                    bad_zone = "ERR"

            writer = csv.writer(file_csv, delimiter=';' if rus_windows else ",")
            if rus_windows or rus_unix or ANDROID:
                writer.writerow(['Resource', 'Geo', 'Url', 'Url_username', 'Status', 'Http_status',
                                 'Deceleration/sec', 'Response/sec', 'Time/sec', 'Session/kB'])
            else:
                writer.writerow(['Resource', 'Geo', 'Url', 'Url_username', 'Status', 'Http_code',
                                 'Deceleration/s', 'Response/s', 'Time/s', 'Session/kB'])

            for site in FULL:
                if FULL[site]['session_size'] == 0:
                    Ssession = "Head"
                elif type(FULL[site]['session_size']) != str:
                    Ssession = str(FULL.get(site).get("session_size")).replace('.', locale.localeconv()['decimal_point'])
                else:
                    Ssession = "Bad"

                writer.writerow([site, FULL[site]['countryCSV'], FULL[site]['url_main'], FULL[site]['url_user'],
                                 FULL[site]['exists'], FULL[site]['http_status'],
                                 FULL[site]['response_time_site_ms'].replace('.', locale.localeconv()['decimal_point']),
                                 FULL[site]['check_time_ms'].replace('.', locale.localeconv()['decimal_point']),
                                 FULL[site]['response_time_ms'].replace('.', locale.localeconv()['decimal_point']),
                                 Ssession])

            writer.writerow(['«' + '-'*35, '-'*4, '-'*35, '-'*56, '-'*13, '-'*17, '-'*37, '-'*17, '-'*28, '-'*15 + '»'])
            writer.writerow([f'DB_(demoversion)={flagBS}_Websites'])
            writer.writerow([f"Nick={usernamCSV}"])
            writer.writerow('')
            writer.writerow([f'Excluded_regions={exl}'])
            writer.writerow([f'Specific_regions_selected={one}'])
            writer.writerow([f"Bad_raw:_{flagBS_err}%_DB,_bad_zone_{bad_zone}" if flagBS_err >= 2 else ''])
            writer.writerow('')
            writer.writerow(['Date'])
            writer.writerow([time.strftime("%Y-%m-%d_%H:%M:%S", TIME_DATE)])
            writer.writerow([f'©2020-{time.localtime().tm_year} «Snoop Project»\n(demo version).'])

            file_csv.close()

            ungzip.clear()
            dic_binding.get("badraw").clear()


## Final output in CLI.
        if bool(FULL) is True:
            direct_results = os.path.join(DIRPATH, "results", "nicknames", "*")
            print(f"{Fore.CYAN}├─Results:{Style.RESET_ALL} found --> {len(find_url_lst)} " + \
                  f"url (session: {time_all}_sec__{s_size_all}_MB)")
            print(f"{Fore.CYAN}├──Saved to:{Style.RESET_ALL} {direct_results}")

            if flagBS_err >= 2: #perc_%
                bad_raw(flagBS_err, bad_zone, nick, [args.exclude_country, args.one_level, args.site_list])
            else:
                print(f"{Fore.CYAN}└───Search date:{Style.RESET_ALL} {time.strftime('%Y-%m-%d__%H:%M:%S', TIME_DATE)}\n")

            if "demo" in VERSION:
                console.print(f"[italic]  Get Snoop Full Version ({web_sites} sites):[/italic]\n[dim yellow]  " + \
                              f"$ {'python ' if 'source' in VERSION else ''}" + \
                              f"{os.path.basename(sys.argv[0])} --donate[/dim yellow]\n", highlight=False)
            elif "full" in VERSION and WINDOWS and not any([args.norm, args.speed, args.one_level, args.site_list]):
                console.print(format_txt(f"[bold red] ![/bold red] [bold yellow]Please note: search speed can be " + \
                                         f"significantly accelerated by using options::[/bold yellow]", k=True, m=True))
                console.print(format_txt(f"[bold yellow]   [-[bold green]-q[/bold green]uick/-[bold green]-p[/bold green]ool/" + \
                                         f"-[bold green]-f[/bold green]ound-print][/bold yellow]", k=True, m=True),
                                         "\n", highlight=False)

            console.print(Panel(f"{E_MAIL} until {date_off}", title='license',
                                style=STL(color="white", bgcolor="blue"),
                                border_style=STL(color="white", bgcolor="blue")))


## Open or not browser with search results.
            if args.no_func is False and exists_counter >= 1:
                try:
                    if not ANDROID:
                        try:
                            webbrowser.open(f"file://{DIRPATH}/results/nicknames/html/{username}.html")
                        except Exception:
                            console.print("[bold red]Unable to open web browser, operating system issues.")
                    else:
                        install_service = Style.DIM + Fore.CYAN + \
                                              "\nTo auto-open results in an external browser on Android, the user " + \
                                              "must have the environment configured, code:" + Style.RESET_ALL + Fore.CYAN + \
                                              "\ncd && pkg install termux-tools; echo 'allow-external-apps=true' >>" + \
                                              ".termux/termux.properties" + Style.RESET_ALL + \
                                              Style.DIM + Fore.CYAN + "\n\nAnd restart the terminal."

                        termux_sv = False
                        if os.path.exists("/data/data/com.termux/files/usr/bin/termux-open"):
                            with open("/data/data/com.termux/files/home/.termux/termux.properties", "r", encoding="utf-8") as f:
                                for line in f:
                                    if ("allow-external-apps" in line and "#" not in line) and line.split("=")[1]\
                                                                                                   .strip()\
                                                                                                   .lower() == "true":
                                        termux_sv = True

                            if termux_sv is True:
                                subprocess.run(f"termux-open {DIRPATH}/results/nicknames/html/{username}.html", shell=True)
                            else:
                                print(install_service)

                        else:
                            print(install_service)
                except Exception:
                    print(f"\n\033[31;1mFailed to open results\033[0m")
        try:
            if len(SQ) == 1:
                hardware.shutdown()
        except Exception:
            pass


## Search by selected users: either from CLI or from file.
    starts(args.username) if args.user is False else starts(user_list)


## Arbeiten...
if __name__ == '__main__':
    try:
        main_cli()
    except KeyboardInterrupt:
        console.print(f"\n[bold red]Interruption [italic](Ctrl + c)[/italic][/bold red]")
        if WINDOWS:
            os.kill(os.getpid(), signal.SIGBREAK)
        elif dic_binding.get('android_lame_workhorse') or MACOS:
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            [pid.terminate() for pid in active_children()]
