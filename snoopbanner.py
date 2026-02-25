#! /usr/bin/env python3
# Copyright (c) 2020 Snoop Project <snoopproject@protonmail.com>
"Text_banner_logo_help"

import base64
import json
import locale
import platform
import sys
import time
import webbrowser

from colorama import Fore, Style, init
from rich.panel import Panel
from rich.console import Console

locale.setlocale(locale.LC_ALL, '')
init(autoreset=True)
console = Console()


## Error logging.
def err_all(err_="low"):
    if err_ == "high":
        return "⚠️ [bold red]Attention! Critical error, please report it to the developer.\nhttps://github.com/snooppr/snoop/issues[/bold red]"
    elif err_ == "low":
        return "⚠️ [bold yellow]Error[/bold yellow]"


## DB.
def DB(db_base):
    try:
        with open(db_base, "r", encoding="utf8") as f_r:
            db = f_r.read()
            db = db.encode("UTF-8")
            db = base64.b64decode(db)
            db = db[::-1]
            db = base64.b64decode(db)
            db_str = db.decode("UTF-8")
            db_str = db_str.replace("errorTypе", "errorType").replace("errоrMsg", "errorMsg")
            trinity = json.loads(db_str)
            return trinity
    except Exception:
        #print(Style.BRIGHT + Fore.RED + "Oops, something went wrong..." + Style.RESET_ALL)
        #sys.exit()
        raise


## Donation.
def donate():
    print("")
    console.print(Panel(f"""[cyan]
╭Donate/Buy:
├──YuMoney:: [white]4100111364257544[/white]
├──Sber_card:: [white]2202208013277075[/white]
├──Raiffeisen_card:: [white]2200300512321074[/white]
└──By phone number (SBP/YuMoney Bank):: [white]+79004753581[white]

[bold green]You can pay for the software using any of the listed payment methods, but the most preferred method is SBP (transfer by phone number without fees from any bank card).

If the user is interested in [red]Snoop demo version[/red], they can purchase [cyan]Snoop full version[/cyan], supporting the development of this IT project[/bold green] [bold cyan]20$[/bold cyan] [bold green]or[/bold green] [bold cyan]1600 RUB.[/bold cyan]
[bold green]When donating/purchasing, specify in the message/email:[/bold green]

    \"\"\"
    [cyan]For the development of Snoop Project: your[/cyan] [bold cyan]e-mail[/bold cyan][cyan],[/cyan]
    [cyan]full[/cyan] [bold cyan]version[/bold cyan] [cyan]for Windows or full version for Linux,[/cyan]
    [bold cyan]status[/bold cyan] [cyan]of user: Individual; Sole Proprietor; Legal Entity (if purchasing software).[/cyan]
    \"\"\"

[bold green]Shortly after, the user will receive a purchase receipt and a download link for the Snoop full version ready build, i.e. an executable file: for Windows — 'snoop_cli.exe', for GNU/Linux — 'snoop_cli.bin'.

Snoop in executable form (build version) is provided under a license that the user must review before purchasing the software.
The license for Snoop Project in executable form is located in the rar archives of the Snoop demo versions at: [/bold green]
[cyan]https://github.com/snooppr/snoop/releases[/cyan][bold green], the license is also available via command::
'[/bold green][cyan]snoop_cli.bin --version[/cyan][bold green]' or '[/bold green][cyan]snoop_cli.exe --version[/cyan][bold green]' for the executable file.

If the software is needed for professional or educational tasks, for example, ten licenses for a university, write a free-form email to the developer.
All students (regardless of institution or field of study) get Snoop full version with a 50% discount.

Snoop full version:
 * 5300+ Websites;
 * support for local and online Snoop database;
 * connection to Snoop DB (online), which is expanded/updated;
 * auto-optimized, fast and aggressive search modes available;
 * user-configurable speed acceleration settings;
 * plugins without restrictions;
 * tech support from the software developer;
 * provision of updated builds;
 * disabled pop-up windows in the HTML report about Snoop demo version.[/bold green]
[bold red]Snoop demo version limitations:
 * Snoop database reduced by > 15x;
 * non-updatable Snoop database;
 * some options/plugins disabled.[/bold red]

[bold green]E-mail:[/bold green] [cyan]snoopproject@protonmail.com[/cyan]
[bold green]Source code:[/bold green] [cyan]https://github.com/snooppr/snoop[/cyan]

❗️[bold yellow] Note that due to censorship, emails from 'mailru' and 'yandex' do not reach the international mail service 'protonmail'. Users of mailru/yandex, send requests to the backup email.[/bold yellow]
[bold green]E-mail: [/bold green][cyan]snoopproject@ya.ru[/cyan]
""",
                        title="[bold red]demo: (Public Offer)",
                        border_style="bold blue"))

    try:
        webbrowser.open("https://yoomoney.ru/to/4100111364257544")
    except Exception:
        print("\033[31;1mFailed to open browser\033[0m")

    print(Style.BRIGHT + Fore.RED + "Exit")
    sys.exit()


## Buy.
def buy():
    donate_buy = """
<script>
function bay() {document.write('\
<html>\
<head>\
\t<title>💳 Donate/Buy Snoop Project</title>\
</head>\
<body style=\\"background-color: #c0c0c0\\">\
<p><span style="color:#009a7c"><big>╭</big><span style="font-size:36px">Donate/Buy</span>:</span><br />\
<span style="color:#009a7c"><big>├──</big>YuMoney::</span> <a href="https://yoomoney.ru/to/4100111364257544" target="_blank">4100111364257544</a><br />\
<span style="color:#009a7c"><big>├──</big>Sber_card:: </span><strong>2202208013277075</strong><br />\
<span style="color:#009a7c"><big>├──</big>Raiffeisen_card:: </span><strong>2200300512321074</strong><br />\
<span style="color:#009a7c"><big>├──</big>By phone number <em>(SBP: YuMoney bank)</em>:: </span><strong>+79004753581</strong><br />\
<span style="color:#009a7c"><big>└──</big>SberBank Online <em>(mobile app)</em>:: </span><strong>QR code</strong><br />\
<img alt="QR code for SberBank Online users only." src="https://raw.githubusercontent.com/snooppr/snoop/refs/heads/master/web/QR_donate_SberBank.png" style="height:200px; width:200px" /></p>\
\
<p><span style="font-size:18px"><span style="color:#007500">You can pay for the software using <u>any payment method</u>, but the most preferred method is SBP <em>(transfer by phone number without fees from any bank card)</em>.</span></span></p>\
\
<p><span style="font-size:18px"><span style="color:#007500">If the user is interested in Snoop demo version, they can purchase <strong>Snoop full version</strong>, supporting the development of this IT project <strong>20$</strong> or <strong>1600 RUB</strong>.<br />\
When donating/purchasing, specify in the message/email:</span></span></p>\
\
<p><span style="font-size:18px">&nbsp;&nbsp;&nbsp; \\&quot;\\&quot;\\&quot;<br />\
<span style="color:#009a7c">&nbsp;&nbsp;&nbsp; For the development of Snoop Project: your <strong>e-mail</strong>,<br />\
&nbsp;&nbsp;&nbsp; full <strong>version</strong> for Windows or full version for Linux,<br />\
&nbsp;&nbsp;&nbsp; <strong>status</strong> of user: Individual; Sole Proprietor; Legal Entity <em>(if purchasing software)</em>.</span><br />\
&nbsp;&nbsp;&nbsp; \\&quot;\\&quot;\\&quot;</span></p>\
\
<p><span style="font-size:18px"><span style="color:#007500">Shortly after, the user will receive a purchase receipt and a download link for the Snoop full version ready build, <br>\
i.e. an executable file: for Windows &mdash; &#39;snoop_cli.exe&#39;, for GNU/Linux &mdash; &#39;snoop_cli.bin&#39;.</span></span></p>\
\
<p><span style="font-size:18px"><span style="color:#007500">Snoop in executable form <em>(build version)</em> is provided under a license that the user must review before purchasing the software.<br />\
The license for Snoop Project in executable form is located in the rar archives of the Snoop demo versions at:</span><br />\
<a href="https://github.com/snooppr/snoop/releases" target="_blank">https://github.com/snooppr/snoop/releases</a> <span style="color:#007500">, the license is also available via command::<br />\
&#39;</span><strong><span style="color:#16a085">snoop_cli.bin --version</span></strong><span style="color:#007500">&#39; or &#39;</span><strong><span style="color:#16a085">snoop_cli.exe --version</span></strong><span style="color:#007500">&#39; for the executable file.</span></span></p>\
\
<p><span style="font-size:18px"><span style="color:#007500">If the software is needed for professional or educational tasks, for example, ten licenses for a university, write a free-form email to the developer.<br />\
All students <em>(regardless of institution or field of study)</em> get Snoop full version with a <strong>50%</strong> discount.</span></span></p>\
\
<p><span style="font-size:18px"><span style="color:#007500">Snoop full version:</span></span></p>\
\
<ul>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;5300+ Websites;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;support for local and online Snoop database;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;connection to Snoop DB (online), which is expanded/updated;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;auto-optimized, fast and aggressive search modes available;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;user-configurable speed acceleration settings;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;plugins without restrictions;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;tech support from the software developer;</span></span></li>\
    <li><span style="font-size:18px"><span style="color:#007500">&nbsp;provision of updated builds;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#007500">&nbsp;disabled pop-up windows in the HTML report about Snoop demo version.</span></span></li>\
</ul>\
\
<p><span style="font-size:18px"><span style="color:#e74c3c">Snoop demo version limitations:</span></span></p>\
\
<ul>\
\t<li><span style="font-size:18px"><span style="color:#e74c3c">Snoop database reduced by &gt; 15x;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#e74c3c">non-updatable Snoop database;</span></span></li>\
\t<li><span style="font-size:18px"><span style="color:#e74c3c">some options/plugins disabled.</span></span></li>\
</ul>\
\
<p><span style="font-size:18px"><span style="color:#007500">E-mail:</span> <span style="color:#009a7c"><strong>snoopproject@protonmail.com</strong></span><br />\
<span style="color:#007500">Source code: </span><a href="https://github.com/snooppr/snoop" target="_blank">https://github.com/snooppr/snoop</a></span></p>\
\
<p><span style="font-size:18px">❗️<span style="color:#e15700">Note that due to censorship, emails from &#39;mailru&#39; and &#39;yandex&#39; do not reach the international mail service &#39;protonmail&#39;. <br>\
Users of mailru/yandex, send requests to the backup email.</span><br />\
<span style="color:#007500">E-mail:</span><span style="color:#009900"> </span><span style="color:#009a7c"><strong>snoopproject@ya.ru</strong></span></span></p>\
<hr />\
<p>Return: &#39;F5&#39;</p>\
</body>\
</html>')}
</script>"""
    return donate_buy

## Logo.
def logo(text, color="\033[31;1m", exit=True):
    if sys.platform != 'win32' or (sys.platform == 'win32' and int(platform.version().split('.')[2]) >= 19045):
        with console.screen():
            console.print(r"""[cyan]
 ____                                      
/\  _`\                                    
\ \,\L\_\    ___     ___     ___   _____   
 \/_\__ \  /' _ `\  / __`\  / __`\/\ '__`\\
   /\ \L\ \/\ \/\ \/\ \_\ \/\ \_\ \ \ \L\ \\
   \ `\____\ \_\ \_\ \____/\ \____/\ \ ,__/
    \/_____/\/_/\/_/\/___/  \/___/  \ \ \/ 
                                     \ \_\\
      __                              \/_/ 
     /\ \                              
     \_\ \     __    ___ ___     ___   
     /'_` \  /'__`\/' __` __`\  / __`\\
    /\ \_\ \/\  __//\ \/\ \/\ \/\ \_\ \\
    \ \___,_\ \____\ \_\ \_\ \_\ \____/
     \/__,_ /\/____/\/_/\/_/\/_/\/___/ 
""")
            time.sleep(1.4)
    for i in text:
        time.sleep(0.04)
        print(f"{color}{i}", end='', flush=True)
    if exit:
        print("\033[31;1m\n\nExit")
        sys.exit()


# snoop.py Help Modules 'if mod == 'help'.
def help_module_1():
    print("""\033[32;1m└──[Help]\033[0m

\033[32;1m========================
| GEO_IP/domain Plugin |
========================\033[0m \033[32m\n
1) Implements online single target search by IP/url/domain and provides statistical information: IPv4/v6; GEO coordinates/link; location.
(Light limited search).

2) Implements online target search by data list: and provides statistical and visualized information: IPv4/v6; GEO coordinates/links; countries/cities; reports in CLI/txt/csv formats; provides visualized report on OSM maps.
(Moderate slow search: request limits:: 15k/hour; does not provide information about providers).

3) Implements offline target search by data list, using DB: and provides statistical and visualized information: IPv4/v6; GEO coordinates/links; locations; providers; reports in CLI/txt/csv formats; provides visualized report on OSM maps.
(Strong and fast search).

Results from methods 1 and 2 may differ and be incomplete - depends on user's personal DNS/IPv6 settings.
Data list — a text file (in utf-8 encoding), which the user specifies as a target, and which contains ip, domain or url (or their combinations).

Plugin purpose — Education/InfoSec.

\033[32;1m============================
| Reverse Vgeocoder Plugin |
============================\033[0m\n
\033[32mReverse impresionante-geocoder from Snoop Project for visualizing coordinates on OSM map with statistical analysis in html/csv/txt formats.

The plugin can extract and process coordinates from any noisy text files. The plugin implements offline target search by given geocoordinates and provides detailed statistical and visualized information (full version).
Increased accuracy for objects in RU; EU; CIS locations relative to the rest of the world.

With this plugin (full version), the user can extract, visualize and analyze information about thousands of geocoordinates in seconds.

Plugin purpose — CTF/Education.\033[0m

\033[32;1m========================
| Yandex_parser Plugin |
========================\033[0m\n
\033[32mThe plugin allows getting information about Yandex service users:
Ya_Reviews; Ya_Q; Ya_Market; Ya_Music; Ya_Dzen; Ya_Disk; E-mail, Name.
And linking the obtained data together at high speed and scale.

The plugin was developed based on the idea and materials of a vulnerability, reports were sent to Yandex as part of the 'Bug Bounty' program in 2020-2021.
Made it to the hall of fame, received financial reward twice, and Yandex fixed the 'bugs' at their discretion.

Plugin purpose — OSINT.

For more details about plugins see 'Snoop Project General Guide.pdf'.\033[0m""")
    console.rule("[bold red]End of help[/bold red]")


# snoopplugins.py Help Module Reverse Vgeocoder 'elif Vgeo == "help"'.
def help_vgeocoder_vgeo():
    print("""\033[32;1m└──[Help]\033[0m
\033[32m
Snoop Project supports two geocoding modes:
[*] Method '\033[32;1mSimple\033[0m\033[32m':: Markers are placed on the OSM map (trimmed HTML report) by coordinates.
All markers are labeled with geotags.
For this method, abbreviated reports with geotags in html/txt formats are available.

[*] Method '\033[32;1mDetailed\033[0m\033[32m':: Markers are placed on the OSM map (HTML report) by coordinates.
All markers are labeled with geotags; countries; districts and cities. Charts by countries/regions, statistics and filtering are available.
Additional reports (tables) are saved with details in [.txt.csv] formats.
This method precisely places markers with geotags, labels them with addresses to the nearest settlements or names of natural objects.
Increased accuracy for objects in RU; EU; CIS locations relative to the rest of the world.

    For example, if a user uploads coordinates pointing to a location near a lake one kilometer from the city of Vyksa, the marker on the OSM map will be placed exactly at the lake, and it will be labeled approximately as:

\"\"\"\033[36m
🌎 Coordinates: 55.342595 42.230801
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Country: RU
Region: Nizhny Novgorod Oblast
District: Ozero Razodeyskoye\033[0m\033[32m
\"\"\"

The method is based on — 'Euclidean tree'.

\033[32;1mReverse Vgeocoder Plugin\033[0m \033[32m- works in offline mode and is equipped with a specially developed geo-DB (some DBs are provided under a free license from download.geonames.org/export/dump/).

    To process data, specify a text file with coordinates in degrees in utf-8 encoding (with .txt extension or no extension). Each line with geocoordinates (latitude, longitude) should be written in the file on a new line (preferably).
Snoop is quite smart: it recognizes and selects geocoordinates separated by commas, spaces, or makes intelligent selection, cleaning out random strings.
    Example geocoordinates file (how a file with coordinates that needs to be specified might look):

\"\"\"\033[36m
51.352,   -108.625
55.466,64.776
52.40662,66.77631
53.028 -104.680
54.505/73.773
Moscow55.75, 37.62 Kaliningrad54.71, 20.51 Rostov-on-Don47.23, 39.72
random_string1, which_will be processed Kazan 55.7734/49.1436
random string2, which will not be processed\033[0m\033[32m
\"\"\"

    After rendering is complete, a web browser will open with the visual result.
All results are saved in '~/.snoop/results/plugins/ReverseVgeocoder/*[.txt.html.csv]'.
For statistical processing of information (sorting by countries/coordinates/raw_data etc.) the user can study the report in csv format.
If charts are not displayed in your HTML report, try opening the report in a different browser.
    This is a convenient plugin if the user needs, for example, not only to process geocoordinates, but also to find chaotic data, or vice versa.""")


# snoopplugins.py Help Module Reverse Vgeocoder 'elif Ya == "help"'.
def help_yandex_parser():
    print("""\033[32;1m└──[Help]

Single-user mode\033[0m
\033[32m[*] Login — the left part before the '@' symbol, for example, bobbimonov@ya.ru, login
'\033[36mbobbimonov\033[0m\033[32m'.
[*] Public Yandex.Disk link — this is a download/view link for materials that the user has made public, for example,
'\033[36mhttps://yadi.sk/d/7C6Z9q_Ds1wXkw\033[0m\033[32m' or '\033[36mhttps://disk.yandex.ru/d/7C6Z9q_Ds1wXkw\033[0m\033[32m'.
[*] Identifier — a hash specified in the url on the user's page, for example, in the Ya.District service: 'https://local.yandex.ru/users/tr6r2c8ea4tvdt3xmpy5atuwg0/' the identifier is '\033[36mtr6r2c8ea4tvdt3xmpy5atuwg0\033[0m\033[32m'.
    Upon successful search completion, a report is displayed in CLI and the user's Yandex pages are opened in the browser.
    The Yandex_parser plugin provides less information by user identifier (compared to other methods), reason — vulnerability fix by Yandex.

\033[32;1mMulti-user mode\033[0m
\033[32m[*] File with usernames — a file (in UTF-8 encoding with .txt extension or without it), containing logins.
Each login in the file should be written on a new line, for example:

\"\"\"
\033[36mbobbimonov
username
username2
username3
random string
bobbimonov@ya.ru
bobbimonov@ya.ru
bobbimonov@ya.ru\033[0m
\033[32m\"\"\"

    When using multi-user mode, upon search completion (fast) an extended report is displayed in CLI, a txt report about Yandex users is saved (with extended, structured data) and a browser opens with a mini report (grouped data).
    The plugin generates but does not check 'availability' of users' personal pages because: frequent Ya.captcha page protection.
All results are saved in '\033[36m~/.snoop/results/plugins/Yandex_parser/*\033[0m\033[32m'\033[0m
    \033[31;1mAt the end of November 2022, Yandex closed the public api, and possibly this plugin will no longer work...\033[0m""")


# snoopplugins.py Help Module GEO_IP/domain 'elif dipbaza'.
def geo_ip_domain():
    print("\033[32;1m└──Help\033[0m\n")
    print("""\033[32m[*] Mode '\033[32;1mOnline search\033[0m\033[32m'. The GEO_IP/domain module from Snoop Project uses a public API and creates statistical and visualized information about the target's ip/url/domain (data array).
    Limitations: requests ~15k/hour, slow data processing speed, no information about providers.
    Advantages of using 'Online search': input data can include not only IP addresses, but also domain/url.
    Example data file (list.txt):

\"\"\"
\033[36m1.1.1.1
2606:2800:220:1:248:1893:25c8:1946
google.com
https://example.org/fo/bar/7564
random string\033[0m
\033[32m\"\"\"\033[0m

\033[32m[*] Mode '\033[32;1mOffline search\033[0m\033[32m'. The GEO_IP/domain module from Snoop Project uses special databases and creates statistical and visualized information about the target's ip (data array, i.e. IP addresses).
Advantages of using 'Offline search': speed (processing thousands of IPs without delays), stability (no dependency on internet connection and user's personal DNS/IPv6 settings), extensive coverage (information about internet providers is provided).

[*] Mode '\033[32;1mOffline_quiet search\033[0m\033[32m'. The same mode as 'Offline', but does not print intermediate data tables to CLI. This mode provides a performance increase of several times.
    Example data file (list.txt):

\"\"\"
\033[36m8.8.8.8
93.184.216.34
2606:2800:220:1:248:1893:25c8:1946
random string\033[0m
\033[32m\"\"\"

    Snoop is quite smart and able to detect and distinguish in input data: IPv4/v6/domain/url, cleaning out errors and random strings.
    After data processing, the user is provided with:
statistical reports in [txt/csv/html and visualized data on OSM map]. If charts are not displayed in your HTML report, try opening the report in a different browser.
    Examples of what the GEO_IP/domain module from Snoop Project can be used for.
For example, if the user has a list of IP addresses from a DDoS attack,
they can analyze where the max/min attack originated from and from whom (providers).
Solving CTF quests where GPS/IPv4/v6 are used.
Ultimately, using the plugin for educational purposes or out of natural curiosity (checking any IP addresses and their association with a provider and location).\033[0m""")
