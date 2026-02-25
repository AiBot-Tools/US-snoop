Snoop Project for Termux
========================

## Snoop Project is one of the most promising OSINT tools — nickname search
- [X] This is the most powerful software taking into account the CIS location.  
• [English readme Snoop for Termux](https://github.com/snooppr/snoop/blob/master/README_android.en.md "Please feel free to improve the translation of this page.")  

<p align="center">  
  <img src="https://raw.githubusercontent.com/snooppr/snoop/master/images/Snoop_2android.png" />  
</p>  

<p align="center">  
  <img src="https://raw.githubusercontent.com/snooppr/snoop/master/images/snoopandroid.png" />  
</p>  

Is your life a Slide-show? Ask snoop.  
Snoop Project was developed without taking into account the opinion of the NSA and their friends, meaning it is accessible to the average user.  

## Building the software yourself from source code  
**Snoop for Android/Demo**  
<p align="center">  
  <img src="https://raw.githubusercontent.com/snooppr/snoop/master/images/Snoop_termux.plugins.png" width="90%" />  
</p>  

**Installation**  

Install [Termux](https://f-droid.org/en/packages/com.termux/ "Termux from F-Droid, Termux is no longer updated on GP!")  
```sh
# NOTE_1!: if the user gets errors during $ 'pkg update', for example because 
# Termux has not been updated for a long time on the user's device,
# then uninstalling/reinstalling the Termux app will not help,
# since after uninstalling the old repositories remain on the user's device, solution:
$ termux-change-repo 
# and choose to receive updates (for all repos) from another mirror repository.

# Open storage access
$ termux-setup-storage

# Install python3 and dependencies
$ apt update && pkg upgrade && pkg install python libcrypt libxml2 libxslt git
$ pip install --upgrade pip

# Clone repository
$ git clone https://github.com/snooppr/snoop

# Enter Snoop working directory
$ cd ~/snoop
# Install 'requirements.txt' dependencies
$ python3 -m pip install -r requirements.txt


# Optional↓
# To expand Termux terminal output (default 2k rows display in CLI), for example, 
# displaying the entire DB option '--list-all [1/2]'
# add line 'terminal-transcript-rows=10000' to '~/.termux/termux.properties' file
# (extremely useful option available in Termux v0.114+). 
# Restart Termux.  

# The user can also run snoop with the 'snoop' command from anywhere in the CLI by creating an alias.  
$ cd && echo "alias snoop='cd && cd snoop && python snoop.py'" >> .bashrc && bash  

# The user can also perform a quick check of an interesting site in the database,  
# without using the "--list-all" option, by using the "snoopcheck" command  
$ cd && echo "alias snoopcheck='cd && cd snoop && echo 2 | python snoop.py --list-all | grep -i'" >> .bashrc && bash  

# NOTE_2!: Snoop is quite smart and can automatically open search results in an external web browser, despite Google restrictions:  
$ cd && pkg install termux-tools; echo 'allow-external-apps=true' >>.termux/termux.properties  
# restart Termux.  
# Upon completion of snoop's search work, to the prompt "what to open search results with", select the built-in Android OS default/system HTMLviewer.  

# NOTE_3!: after disconnecting the Russian Federation from the London Internet Exchange point, Snoop search speed
# (possibly also from other connection providers) on Megafon/Yota dropped by ~2 times.
```
NOTE_4!: if the user has a defective Android (meaning OS version 12+ with multiple restrictions) and it breaks Termux, read the instruction on how to solve the problem [here](https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md#how-to-disable-the-phantom-processes-killing).  
NOTE_5!: old patched python versions 3.7-3.11 are supported from [termux_tur repo](https://github.com/termux-user-repository/tur/tree/master/tur).  

<p align="center">  
  <img src="https://raw.githubusercontent.com/snooppr/snoop/master/images/snoop_alias.gif" width="40%" />  
</p>  


## Usage
```
usage: python3 snoop.py [search arguments...] nickname
or
usage: python3 snoop.py [service arguments | plugins arguments]


service arguments:
  --version, -V         About: print software version, snoop info
                        and License.
  --list-all, -l        Print detailed information about the Snoop
                        database.
  --donate, -d          Donate to the development of the Snoop Project,
                        get/purchase Snoop full version.
  --autoclean, -a       Delete all reports, clear cache.
  --update, -U          Update Snoop.

plugins arguments:
  --module, -m          OSINT search: utilize various Snoop plugins
                        :: IP/GEO/YANDEX.

search arguments:
  nickname              Nickname of the sought user.
                        Simultaneous search for multiple names is supported.
                        A nick containing a space in its name is enclosed in
                        quotes.
  --web-base, -w        Connect to the dynamically updated web_DB (5300+ sites)
                        to search for 'nickname'.
  --site , -s <site_name> 
                        Specify a site name from the '--list-all' DB. Search
                        'nickname' on one specified resource, it is allowed
                        to use the '-s' option multiple times.
  --exclude , -e <country_code> 
                        Exclude selected region from search,
                        it is allowed to use the '-e' option multiple times,
                        for example, '-e RU -e WR' exclude Russia and the
                        World from search.
  --include , -i <country_code> 
                        Include only selected region in search,
                        it is allowed to use the '-i' option multiple times,
                        for example, '-i US -i UA' search in USA and Ukraine.
  --time-out , -t <digit> 
                        Set max waiting time for response from
                        server (seconds). Affects the duration of the search
                        and 'timeout errors' (default is 9 sec).
  --country-sort, -c    Print and record results by countries, not
                        alphabetically.
  --no-func, -n         ✓Monochrome terminal, do not use colors in url
                        ✓Disable opening web browser
                        ✓Disable printing country flags
                        ✓Disable indication and progress status.
  --found-print, -f     Print only found accounts.
  --verbose, -v         During 'nickname' search, print
                        detailed verbalization.
  --userlist , -u <file> 
                        Specify a file with a list of users. Snoop
                        will intelligently process the data and provide
                        additional reports.
  --save-page, -S       Save found user pages to
                        local html-files, slow mode.
  --pool , -p <digit>   Disable auto-optimization and manually set
                        search speed from 1 to 300 max processes. By
                        default, a high load on computer resources is used
                        in Quick mode, in other modes moderate
                        capacity consumption is used. A value too low or
                        too high can significantly slow down the software.
                        ~Calculated optimal value for this
                        device is output in 'snoop info', parameter
                        'Recommended pool', option [--version/-V]. It is
                        suggested to use this option 1) if the user has
                        a multi-core computer and Ram margin or vice versa
                        a weak, rented VPS 2) to speed up or slow down search,
                        recommended in tandem with the [--found-print/-f] option.
  --quick, -q           Fast and aggressive search mode. Does not process
                        failing resources repeatedly, resulting in an accelerated
                        search, but Bad_raw increases slightly.
                        Quick mode adapts to PC power, does not print
                        intermediate results, is effective and
                        intended for Snoop full version.
```


**Examples**
```sh
# To search for only one user:
$ python3 snoop.py username1
# Or, for example, Cyrillic is supported:
$ python3 snoop.py olesya
# To search for a name containing a space:
$ python3 snoop.py "ivan ivanov"
$ python3 snoop.py ivan_ivanov
$ python3 snoop.py ivan-ivanov

# To search for one or more users:
$ python3 snoop.py username1 username2 username3 username4

# Search for multiple users — sort the output of results by countries;
# avoid long hangs on sites (most often the 'dead zone' depends on your ip-address);
# print only found accounts; save pages of found
# accounts locally; specify a file with a list of sought accounts;
# connect to the expandable and updatable Snoop web-base for search:
$ python3 snoop.py -c -t 9 -f -S -u ~/file.txt -w

# Search for two usernames on two resources:
$ python snoop.py -s habr -s lichess chikamaria irina

# Get Snoop full version:
$ python snoop.py --donate
```
**'ctrl + c'** — interrupt search (stop software correctly).  

Results will be saved in '/storage/emulated/0/snoop/results/nicknames/*{txt|csv|html}'.  
open csv in *office, field separator is **comma**.  

Destroy **all** search results — delete the '~/snoop/results' directory.  
or ```python snoop.py --autoclean```

```sh
# Update Snoop to test new features in the software:
$ python3 snoop.py --update #Git installation is required.
```

**Example of snoop for Android/Termux work**  
<p align="center">  
  <img src="https://raw.githubusercontent.com/snooppr/snoop/master/images/Android%20snoop_run.gif" width="40%" />  
</p>  

 • **Aggressive compression of the repository was performed on December 11, 2024.** Full history backup saved.
 Users building Snoop from source code must do 'git clone' anew.  
