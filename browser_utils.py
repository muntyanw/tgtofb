import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from log import log_and_print
import time
import os
from selenium.common.exceptions import TimeoutException
import markdown
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import random

def find_post_input(driver, xpaths, timeout=10):
    """
    Tries to find a contenteditable input field by a list of possible aria-label texts.
    Returns the WebElement if found.
    Raises TimeoutException if none found.
    """
    for xpath in xpaths:
        try:
            log_and_print(f"Пошук '{xpath}'...")
            post_input = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath)
                )
            )
            log_and_print(f"Поле '{xpath}' знайдено та активовано.")
            post_input.click()
            time.sleep(3)
            return post_input
        except TimeoutException:
            log_and_print(f"Поле '{xpath}' не знайдено, пробую наступне...")

    # If we exit the loop without returning
    raise TimeoutException("Жодне з полів не знайдено.")

def find_and_click_by_xpaths(driver, xpaths):
    """
    Tries to find and click an element by a list of XPATHs.
    Clicks the first found element.
    Raises NoSuchElementException if none found.
    """
    for xpath in xpaths:
        try:
            log_and_print(f"Пробую знайти елемент по XPATH: {xpath}")
            element = driver.find_element(By.XPATH, xpath)
            element.click()
            log_and_print(f"Елемент знайдено та клікнуто: {xpath}")
            time.sleep(3)
            return element
        except NoSuchElementException:
            log_and_print(f"Елемент не знайдено по XPATH: {xpath}, пробую наступний...")

    # Якщо жоден не знайдено
    raise NoSuchElementException("Жоден з елементів не знайдено за наданими XPATH.")


CHROME_PORT = 9222  # Порт для отладки
CHROME_DATA_DIR = os.path.abspath("./chrome-data")  # Каталог для данных пользователя
drivers = {}

def get_random_value(array):
    if not array:  # Проверка на пустой массив
        return None
    return random.choice(array)

def convert_markdown_to_html(markdown_text):
    # Конвертация Markdown в HTML
    html_text = markdown.markdown(markdown_text)
    return html_text

def start_chrome_new(driver_path, chromedriver_port):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--remote-debugging-port={chromedriver_port}")
    chrome_options.add_argument(f"--user-data-dir={CHROME_DATA_DIR}")  # Сохранение данных пользователя
    chrome_options.add_argument("--disable-usb")
    chrome_options.add_argument("--disable-usb-keyboard-detect")
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        log_and_print("Запущена новая сессия Chrome.", 'info')
        return driver
    except Exception as e:
        log_and_print(f"Ошибка при запуске новой сессии Chrome: {e}", 'error')
        return None

def start_chrome_with_retries(driver_path, chromedriver_port, retries=3):
    """Функция для запуска Chrome с заданным количеством попыток."""
    for attempt in range(retries):
        try:
            driver = start_chrome_new(driver_path, chromedriver_port)
            if driver:
                return driver
        except Exception as e:
            log_and_print(f"Ошибка при запуске Chrome (попытка {attempt + 1}/{retries}): {e}", 'error')
        time.sleep(5)  # Задержка перед повторной попыткой
    log_and_print("Не удалось запустить Chrome после нескольких попыток.", 'error')
    return None

def autorizeFb(driver, login_fb, pass_fb, time_wait_login):
    log_and_print("Открытие страницы Facebook...", 'info')
    driver.get('https://www.facebook.com/')
    time.sleep(2)

    try:
        log_and_print("Спроба авторізаціі.", 'info')
        username = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        password = driver.find_element(By.ID, 'pass')

        log_and_print("Ввод логина и пароля...", 'info')
        username.send_keys(login_fb)
        password.send_keys(pass_fb)
        password.send_keys(Keys.RETURN)

        WebDriverWait(driver, time_wait_login).until(
            EC.url_contains("https://www.facebook.com/")
        )
        log_and_print("Авторизация прошла успешно.", 'info')
    except TimeoutException:
        log_and_print("Ошибка авторизации.", 'error')

def remove_non_bmp_characters(text):
    return ''.join(char for char in text if ord(char) <= 0xFFFF)

def publichOneMessage(driver, group_id, message, xpaths, image_path=None, fone_colors=None):
    group_url = f'https://www.facebook.com/groups/{group_id}'
    log_and_print(f"Переход на страницу группы: {group_url}", 'info')
    driver.get(group_url)
    time.sleep(5)

    log_and_print("Поиск элемента для начала публикации...", 'info')
    
    find_post_input(driver, xpaths["xpath_start_publication"], timeout=15)
   
    time.sleep(2)

    post_input = None

    log_and_print("Пошук вікна для ввода текста…", 'info')
    post_input = find_post_input(driver, xpaths["xpath_publication"], timeout=10)
    time.sleep(3)

    try:
        cleaned_message = remove_non_bmp_characters(message)
        log_and_print(f"Ввод текста сообщения: {cleaned_message}", 'info')
        post_input.send_keys(cleaned_message)
        time.sleep(2)
        
        find_and_click_by_xpaths(driver, xpaths["xpath_element_pub1"])

        find_and_click_by_xpaths(driver, xpaths["xpath_element_pub2"])
        
        # Генерация всех сочетаний
        prepared_xpaths = [
            xpath_template.format(fone_color=fone_color)
            for xpath_template in xpaths["xpath_element_pub3"]
            for fone_color in fone_colors
        ]
        log_and_print(prepared_xpaths)
        # Перемешивание в случайном порядке
        random.shuffle(prepared_xpaths)
        
        find_and_click_by_xpaths(driver, prepared_xpaths)

        # Если указан путь к изображению, загружаем его
        if image_path and os.path.exists(image_path):
            log_and_print(f"Загрузка изображения: {image_path}", 'info')

            try:
                # Клик по кнопке "Дополните публикацию"
                find_post_input(driver, xpaths["xpath_element_pub4"])
                # Клик по кнопке "Фото/видео"
                find_post_input(driver, xpaths["xpath_element_pub5"])

                sel = xpaths["xpath_element_pub5"]
                file_inputs = driver.find_elements(By.XPATH, sel)

                if file_inputs:
                    # Выбираем первый из найденных
                    image_upload_input = file_inputs[0]
                    image_upload_input.send_keys(image_path)
                    log_and_print("Изображение успешно загружено через скрытый input.", 'info')
                else:
                    print("Не удалось найти элементы для загрузки файлов.")

                time.sleep(5)  # Задержка для завершения загрузки

            except Exception as e:
                log_and_print(f"Ошибка при загрузке изображения: {e}", 'error')

        find_post_input(driver, xpaths["xpath_element_pub7"])

    except Exception as e:
        log_and_print(f"Не удалось отправить сообщение, ошибка: {e}", 'error')

def sendOneMessagessToFb(message, fb_creds, fb_groups, fone_colors, chromedriver_port, time_wait_login, xpaths, image_path=None):
    global drivers
    current_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(current_dir, 'chromedriver.exe')
    log_and_print(f"driver_path: {driver_path}", 'info')

    for login_fb, user_data in fb_groups.items():
        log_and_print(f"Пользователь: {login_fb}", 'info')
        pass_fb = fb_creds.get(login_fb, {}).get('password')

        if drivers.get(login_fb) is None:
            drivers[login_fb] = start_chrome_with_retries(driver_path, chromedriver_port)

            if drivers[login_fb] is None:
                log_and_print("Не удалось запустить или подключиться к браузеру.", 'error')
                continue  # Переходим к следующему пользователю, если запуск не удался

            autorizeFb(drivers[login_fb], login_fb, pass_fb, time_wait_login)

        for group_id, group_data in user_data.get('groups', {}).items():
            pause_seconds = group_data.get('pause_seconds', 5)
            try:
                publichOneMessage(drivers[login_fb], group_id, message, xpaths, image_path, fone_colors)
            except Exception as e:
                log_and_print(f"Ошибка при публикации: {e}", 'error')
                # Перезапускаем драйвер при возникновении ошибки
                drivers[login_fb] = start_chrome_with_retries(driver_path, chromedriver_port)
                if drivers[login_fb] is None:
                    log_and_print("Не удалось перезапустить драйвер. Переход к следующему пользователю.", 'error')
                    break  # Переходим к следующему пользователю, если перезапуск не удался
            finally:
                log_and_print(f"Пауза: {pause_seconds} секунд", 'info')
                time.sleep(pause_seconds)

    log_and_print("Оставляем браузер открытым.", 'info')
