import requests
import time
import urllib.parse
import re
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telebot

load_dotenv()

users = ['getfitbyline','malak_belkacem', 'g.athleticstudio', 'nadia__sedki', 'sara.sedkix', 'maryanagharibb', 'beki_ksri',
          'rymfikri', 'afrasaracoglu', 'dhuratadoraspage', 'lil._.cassie', 'osallak.interior',
          'cristiana.love', 'aya_jul1', 'melisadongel', 'caterina__petracca', 'kawtarbamo', 'alliesherlock',
          'mandysacs', 'dhurkidoraa_fan', 'bodydesigner', 'luxurygirl.live', 'akinemre_',
          'saocurious', 'bessan.lsmail', 'helga_model', 'indiimustafa', 'solazolareal', 'miraslava.kostyeva',
          'xenia', 'kendalljenner', 'kellyvedovelli', 'jouhinamarlini', 'handemiyy', 'daniellasalvi',
          'narins_beauty', 'cedrabeauty', 'sherinsbeauty', 'burcuozberk', 'ozgeyagizz', 'melisapamuk',
          '_moravskka', 'hazalfilizkucukkose', 'dhuratadora', 'iamyanetgarcia', 'aycaaysinturan', 'sommerray',
          'norafatehi', 'cathykelley', 'iamenisa', 'gigihadid', 'georginagio', 'karolg', 'tassanakrit',
          'aalyahgutierrez', 'lanarose786', 'demetozdemir', 'bensusoral', 'mercedes_ns',
          'majda_bouhaidoura', 'annemarie', 'billieeilish', 'denizbaysal_', 'naiss_officiel_48', 'berbich_sofia',
          'iam_evaqueen', 'olhafatiuk', 'sedef.bekiroglu', 'madisonbeer', 'kayaozgu', 'neslihanatagul',
          'noursaw', 'mariahnadim', 'thecjperry', 'melimtx', 'carolinemarlini', 'amandacerny', 'serdarsanal',
          'yasin_yazici', 'keremmsoyler', 'dilandeniz', 'nadineladki14', 'malutrevejo', 'gamze_ercel', 'faouzia',
          'elouadilea', 'elcinsangu', 'haileybieber', 'dualipa', 'selenagomez', 'evcenf', 'catitttaisi', 'kyliejenner']

chatId = os.getenv('CHAT_ID')
bot_token = os.getenv('BOT_TOKEN')
SENT_FILE = os.getenv("SENT_FILE", "sent_media.txt")

bot = telebot.TeleBot(bot_token)

# Load already sent media
try:
    with open(SENT_FILE, "r") as f:
        sent_media = set(line.strip() for line in f.readlines())
except FileNotFoundError:
    sent_media = set()


def extract_media_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    media_param = query.get("media")
    
    if media_param:
        decoded = urllib.parse.unquote(media_param[0])
    else:
        decoded = url

    return decoded.replace("\\", "").strip('"')


def extract_media_hash(url: str) -> str:
    match = re.search(r'/([^/]+\.(?:mp4|jpg|webp))', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("No media hash found in the URL")


def isitvideo(url: str) -> bool:
    video_extensions = ('.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.webm')
    url = url.lower()
    return any(ext in url for ext in video_extensions)


def download_media(url: str, folder: str = "downloads") -> str:
    """Download media to a local folder and return local file path."""
    os.makedirs(folder, exist_ok=True)
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        filename = extract_media_hash(url)
        local_path = os.path.join(folder, filename)
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(1024 * 1024):
                f.write(chunk)
        return local_path
    except Exception as e:
        print(f"❌ Failed to download media: {url} ({e})")
        return None


def sendmedia_with_fallback(url, chatId, caption=None):
    """Try sending via URL first, fallback to local download if fails."""
    try:
        if isitvideo(url):
            bot.send_video(chatId, url, caption=caption)
        else:
            bot.send_photo(chatId, url, caption=caption)
        print(f"✅ Sent via URL for: {caption}")
    except Exception as e:
        print(f"⚠️ Failed to send via URL for {caption}: {url} ({e})")
        local_file = download_media(url)
        if not local_file:
            return
        try:
            with open(local_file, "rb") as f:
                if isitvideo(local_file):
                    bot.send_video(chatId, f, caption=caption)
                else:
                    bot.send_photo(chatId, f, caption=caption)
            print(f"✅ Sent via local file for: {caption}")
        except Exception as e:
            print(f"❌ Failed to send local file {local_file}: {e}")
        finally:
            if os.path.exists(local_file):
                os.remove(local_file)


def getusername(username: str) -> list:
    headers = {
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
        'content-type': 'application/x-www-form-urlencoded',
        'priority': 'u=1, i',
        'referer': 'https://storiesdown.org/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    }

    params = {
        'url': username,
        'method': 'allstories',
    }

    response = requests.get('https://storiesdown.org/content.php', params=params, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    links = []
    for tag in soup.find_all(['img', 'source']):
        src = tag.get('src')
        if src:
            link = extract_media_url(src)
            try:
                media_hash = extract_media_hash(link)
                if media_hash not in sent_media:
                    links.append(link)
            except ValueError:
                print(f"⚠️ Could not extract hash from URL: {link}")
    return links


def fetch_stories(username, chatId):
    media_links = getusername(username)
    if not media_links:
        print(f"ℹ️ No stories found for {username}")
        return

    for link in media_links:
        try:
            media_hash = extract_media_hash(link)
            sendmedia_with_fallback(link, chatId, caption=username)
            sent_media.add(media_hash)
            with open(SENT_FILE, "a") as f:
                f.write(media_hash + "\n")
        except ValueError:
            print(f"⚠️ Skipped invalid media URL: {link}")
        time.sleep(2)


def main():
    for user in users:
        try:
            fetch_stories(user, chatId)
            print("⏸️ Waiting 10 seconds before next user...")
            time.sleep(10)
        except Exception as e:
            print(f"❌ Failed for {user}: {e}")


if __name__ == "__main__":
    main()
