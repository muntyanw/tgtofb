import json
from log import log_and_print

tg_creds = None
tg_channels = None
fb_creds = None
fb_groups = None

def load_json(file_path):
    log_and_print(f"Загрузка данных из JSON файла {file_path}.", 'info')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        log_and_print(f"Данные успешно загружены из {file_path}.", 'info')
        return data
    except FileNotFoundError:
        log_and_print(f"Файл {file_path} не найден.", 'error')
        return None
    except json.JSONDecodeError:
        log_and_print(f"Ошибка декодирования JSON в файле {file_path}.", 'error')
        return None

def init():
    global tg_creds
    global tg_channels
    global fb_creds
    global fb_groups

    creds = load_json('creds.json')
    fb_creds = creds.get('fb_creds', {})
    log_and_print(f"fb_creds {fb_creds}.", 'info')
    tg_creds = creds.get('tg_creds', {})
    log_and_print(f"tg_creds {tg_creds}.", 'info')

    fb_groups = load_json('fb_groups.json')
    log_and_print(f"fb_groups {fb_groups}.", 'info')
    tg_channels = load_json('tg_channels.json')
    log_and_print(f"tg_channels {tg_channels}.", 'info')

    return tg_creds, fb_creds, fb_groups, tg_channels