import urllib.request
import xml.etree.ElementTree as ET
import re

playlist_url = "https://pl.ottg.me/get.php?username=adgeuk&password=GYXCH4DBLZ&type=m3u&output=hls&censored=0"
epg_url = "http://epg.uspeh.my/epg.xml"

print("Скачиваю плейлист...")
req = urllib.request.urlopen(playlist_url)
playlist_content = req.read().decode('utf-8')

print("Скачиваю EPG (это может занять пару секунд, файл большой)...")
urllib.request.urlretrieve(epg_url, "source.xml")

print("Анализирую каналы...")
# Парсим EPG каналы
tree = ET.parse("source.xml")
root = tree.getroot()

epg_channels = {}
for channel in root.findall('channel'):
    ch_id = channel.get('id')
    name_elem = channel.find('display-name')
    if name_elem is not None and name_elem.text:
        clean_name = re.sub(r'[^а-яa-z0-9]', '', name_elem.text.lower())
        epg_channels[clean_name] = ch_id

# Ищем совпадения в плейлисте
matches = {}
current_tvg_id = None
for line in playlist_content.splitlines():
    if line.startswith('#EXTINF:'):
        # Ищем tvg-id в плейлисте
        match_id = re.search(r'tvg-id="([^"]+)"', line)
        if match_id:
            current_tvg_id = match_id.group(1)
        
        # Извлекаем название канала (обычно идет после запятой в конце строки)
        parts = line.split(',')
        if len(parts) > 1 and current_tvg_id:
            channel_name = parts[-1]
            clean_p_name = re.sub(r'[^а-яa-z0-9]', '', channel_name.lower())
            if clean_p_name in epg_channels:
                matches[epg_channels[clean_p_name]] = current_tvg_id

print(f"Найдено автоматических совпадений: {len(matches)}")
