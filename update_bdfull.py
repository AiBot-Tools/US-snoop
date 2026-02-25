import csv
import io
import json
import base64
import re

csv_data = """website_app_name,user_address
4chan,"N/A (no public user profile URL)"
8kun,"N/A (no public user profile URL)"
Amino,https://aminoapps.com/u/{username}
ArtStation,https://www.artstation.com/{username}
Badoo,https://badoo.com/profile/{id}
Baidu Tieba,https://tieba.baidu.com/home/main?un={username}
Bandcamp,https://{username}.bandcamp.com
Behance,https://www.behance.net/{username}
BeReal,"N/A (no stable public web user profile URL)"
Bigo Live,https://www.bigo.tv/user/{uid}
BitChute,https://www.bitchute.com/channel/{channel_slug}/
Bluesky,https://bsky.app/profile/{handle}
Bridgefy,"N/A (no public web user profile URL)"
Bumble,"N/A (no public web user profile URL)"
Clapper,"N/A (no universally stable public username URL)"
Classmates.com,https://www.classmates.com/profile/{id}
Clubhouse,https://www.clubhouse.com/@{username}
Couchsurfing,https://www.couchsurfing.com/people/{username_or_id}
Dailymotion,https://www.dailymotion.com/{username}
DeviantArt,https://www.deviantart.com/{username}
Discord,"N/A (no public global user profile URL)"
Douban,https://www.douban.com/people/{username}/
Doximity,"N/A (no standard public user URL)"
Dribbble,https://dribbble.com/{username}
eHarmony,"N/A (no public web user profile URL)"
Element,"N/A (client/server dependent; Matrix ID format: @user:server.tld)"
Fandom,https://{wiki}.fandom.com/wiki/User:{username}
Facebook,https://www.facebook.com/{username}
Facebook Messenger,https://m.me/{username}
Feeld,"N/A (no public web user profile URL)"
FetLife,https://fetlife.com/users/{user_id}
Fitbit Community,https://community.fitbit.com/t5/user/viewprofilepage/user-id/{id}
Flickr,https://www.flickr.com/people/{username_or_nsid}/
Gab,https://gab.com/{username}
Garmin Connect,https://connect.garmin.com/modern/profile/{uuid}
Geneanet,https://www.geneanet.org/profil/{username}
GIPHY,https://giphy.com/@{username}
GitHub Discussions,https://github.com/{username}
Gitter,"N/A (room-centric; no standard public user URL)"
Glass,https://glass.photo/{username}
Goodreads,https://www.goodreads.com/user/show/{id}-{slug}
Google Chat,"N/A (no public web user profile URL)"
Google Meet,"N/A (no public web user profile URL)"
Google Messages,"N/A (no public web user profile URL)"
Grindr,"N/A (no public web user profile URL)"
GroupMe,"N/A (no public web user profile URL)"
HelloTalk,"N/A (no universally stable public username URL)"
Hinge,"N/A (no public web user profile URL)"
Houseparty,"N/A (discontinued / no current public profile URL)"
ICQ,"N/A (no standard current public web user profile URL)"
iMessage,"N/A (no public web user profile URL)"
Imgur,https://imgur.com/user/{username}
Instagram,https://www.instagram.com/{username}/
KakaoTalk,"N/A (no public web user profile URL)"
Kick,https://kick.com/{username}
Kik,"N/A (no public web user profile URL)"
Koo,https://www.kooapp.com/profile/{username}
Letterboxd,https://letterboxd.com/{username}/
Life360,"N/A (no public web user profile URL)"
LINE,"N/A (no standard public user profile URL)"
LINE VOOM,https://linevoom.line.me/user/{id}
LinkedIn,https://www.linkedin.com/in/{username}/
Marco Polo,"N/A (no public web user profile URL)"
Mastodon,https://{instance}/@{username}
Medium,https://medium.com/@{username}
MeWe,https://mewe.com/i/{username}
Microsoft Teams,"N/A (no public web user profile URL)"
Minds,https://www.minds.com/{username}
Naver BAND,"N/A (group-centric / no universal public username URL)"
Nextdoor,"N/A (no public web user profile URL)"
Nostr,"N/A (client-dependent; e.g., https://primal.net/p/{npub})"
Odnoklassniki,https://ok.ru/{username_or_id}
Odysee,https://odysee.com/@{username}
OkCupid,https://www.okcupid.com/profile/{username}
OnlyFans,https://onlyfans.com/{username}
Patreon,https://www.patreon.com/{username}
Pinterest,https://www.pinterest.com/{username}/
Plenty of Fish,"N/A (no stable public web user profile URL)"
QQ,"N/A (no standard public username URL)"
Quora,https://www.quora.com/profile/{display-name}
Reddit,https://www.reddit.com/user/{username}/
Rumble,https://rumble.com/user/{username}
Session,"N/A (no public web user profile URL)"
Signal,"N/A (no public web user profile URL)"
Skype,"N/A (no standard public profile URL)"
Slack,https://{workspace}.slack.com/team/{user_id}
Snapchat,https://www.snapchat.com/add/{username}
SoundCloud,https://soundcloud.com/{username}
Substack Notes,https://substack.com/@{username}
Telegram,https://t.me/{username}
Threads,https://www.threads.net/@{username}
TikTok,https://www.tiktok.com/@{username}
Tinder,"N/A (no public web user profile URL)"
Truth Social,https://truthsocial.com/@{username}
Tumblr,https://{username}.tumblr.com
Twitch,https://www.twitch.tv/{username}
UpScrolled,"N/A (no verified universal public username URL pattern)"
Viber,"N/A (no public personal profile URL)"
Vimeo,https://vimeo.com/{username}
VK,https://vk.com/{username}
VSCO,https://vsco.co/{username}
Wattpad,https://www.wattpad.com/user/{username}
WeChat,"N/A (no public web user profile URL)"
Weibo,https://weibo.com/u/{uid}
WhatsApp,https://wa.me/{phone_number}
X,https://x.com/{username}
Yik Yak,"N/A (no public web user profile URL)"
YouTube,https://www.youtube.com/@{handle}
Zoom,https://zoom.us/my/{personalname}"""

def load_db(path):
    with open(path, 'r', encoding='utf8') as f:
        db = f.read().encode('UTF-8')
        db = base64.b64decode(db)
        db = db[::-1]
        db = base64.b64decode(db)
        return json.loads(db.decode('UTF-8'))

def save_db(path, j):
    db_str = json.dumps(j, ensure_ascii=False, indent=2, separators=(',', ': '))
    db = db_str.encode('UTF-8')
    db = base64.b64encode(db)
    db = db[::-1]
    db = base64.b64encode(db)
    with open(path, 'w', encoding='utf8') as f:
        f.write(db.decode('UTF-8'))

def main():
    bd = load_db('BDfull')
    reader = csv.reader(io.StringIO(csv_data))
    header = next(reader)
    
    # Get a template for missing keys
    template = bd['11x2'].copy()
    
    incompatible = []
    
    for row in reader:
        name, url = row
        if '{username}' not in url:
            incompatible.append(f"{name},{url}")
        else:
            bd_url = url.replace('{username}', '{}')
            m = re.match(r'(https?://[^/]+)', url)
            urlMain = m.group(1) if m else url
            
            if name in bd:
                bd[name]['url'] = bd_url
                bd[name]['urlMain'] = urlMain
            else:
                new_entry = template.copy()
                new_entry['url'] = bd_url
                new_entry['urlMain'] = urlMain
                new_entry['errorTyp\u0435'] = 'status_code'
                bd[name] = new_entry
                
    save_db('BDfull', bd)
    
    with open('NotCompatible.md', 'w', encoding='utf-8') as f:
        f.write("# Incompatible URLs\n\n")
        f.write("The following websites/apps do not use the `{username}` placeholder in their URLs:\n\n")
        f.write("website_app_name,user_address\n")
        for item in incompatible:
            f.write(item + "\n")

    print(f"Added {len(list(reader)) - len(incompatible)} compatible entries to BDfull")
    print(f"Wrote {len(incompatible)} incompatible entries to NotCompatible.md")

if __name__ == '__main__':
    main()
