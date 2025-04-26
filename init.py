import json
from log import log_and_print
import os
import sys

tg_creds = None
tg_channels = None
fb_creds = None
fb_groups = None
settings = None

def resource_path(relative_path):
    """ Получить абсолютный путь к ресурсу, работает и в dev и в PyInstaller onefile """
    if getattr(sys, 'frozen', False):
        # Если запущено как .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт .py
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_json(filename):
    path = resource_path(filename)
    print(f"Загрузка данных из JSON файла {path}.")
    if not os.path.exists(path):
        print(f"Файл {filename} не найден.")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def init():
    global tg_creds
    global tg_channels
    global fb_creds
    global fb_groups
    global settings

    creds = load_json('creds.json')
    fb_creds = creds.get('fb_creds', {})
    log_and_print(f"fb_creds {fb_creds}.", 'info')
    tg_creds = creds.get('tg_creds', {})
    log_and_print(f"tg_creds {tg_creds}.", 'info')

    fb_groups = load_json('fb_groups.json')
    log_and_print(f"fb_groups {fb_groups}.", 'info')
    tg_channels = load_json('tg_channels.json')
    log_and_print(f"tg_channels {tg_channels}.", 'info')
    settings = load_json('settings.json')
    log_and_print(f"settings {tg_channels}.", 'info')

    return tg_creds, fb_creds, fb_groups, tg_channels, settings