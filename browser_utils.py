from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from log import log_and_print
import time

def autorizeFb(driver, login_fb, pass_fb):
    log_and_print("Открытие страницы Facebook...", 'info')
    driver.get('https://www.facebook.com/')
    time.sleep(2)

    log_and_print("Ожидание появления полей для логина и пароля...", 'info')
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'email'))
    )
    password = driver.find_element(By.ID, 'pass')

    log_and_print("Ввод логина и пароля...", 'info')
    username.send_keys(login_fb)
    password.send_keys(pass_fb)
    password.send_keys(Keys.RETURN)

    log_and_print("Ожидание завершения авторизации...", 'info')
    WebDriverWait(driver, 15).until(
        EC.url_contains("https://www.facebook.com/")
    )
    log_and_print("Авторизация прошла успешно.", 'info')

def publichOneMessage(driver, group_id, message):
    # Открытие группы
    group_url = f'https://www.facebook.com/groups/{group_id}'
    log_and_print(f"Переход на страницу группы: {group_url}", 'info')
    driver.get(group_url)
    time.sleep(5)

    # Поиск и клик по элементу "Напишите что-нибудь..."
    log_and_print("Поиск элемента для начала публикации...", 'info')
    post_box_trigger = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Напишите что-нибудь...']"))
    )
    post_box_trigger.click()
    log_and_print("Элемент 'Напишите что-нибудь...' найден и активирован.", 'info')

    # Ожидание появления текстового поля для ввода
    log_and_print("Ожидание текстового поля для ввода публикации...", 'info')
    post_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@aria-label='Создайте общедоступную публикацию…' and @contenteditable='true']"))
    )
    post_input.click()
    log_and_print("Поле для ввода текста найдено и активировано.", 'info')

    # Ввод текста в поле публикации
    log_and_print("Ввод текста сообщения...", 'info')
    post_input.send_keys(message)
    time.sleep(2)

    # Поиск и клик по кнопке "Опубликовать"
    log_and_print("Поиск кнопки 'Опубликовать'...", 'info')
    post_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Отправить']"))
    )
    post_button.click()
    log_and_print("Сообщение успешно опубликовано!", 'info')


def sendOneMessagessToFb(message, fb_creds, fb_groups):

    log_and_print("Настройка опций для Chrome (отключение уведомлений)", 'info')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-notifications")

    # Цикл по пользователям
    for login_fb, user_data in fb_groups.items():
        log_and_print("Запуск веб-драйвера с опциями", 'info')
        driver = webdriver.Chrome(options=chrome_options)

        log_and_print(f"Пользователь: {login_fb}", 'info')
        pass_fb = fb_creds.get(login_fb, {}).get('password')

        autorizeFb(driver, login_fb, pass_fb)

        # Цикл по группам внутри пользователя
        groups = user_data.get('groups', {})
        for group_id, group_data in groups.items():
            pause_seconds = group_data.get('pause_seconds')
            try:
                publichOneMessage(driver, group_id, message)
            except Exception as e:
                log_and_print(f"Общая ошибка: {e}", 'error')
            finally:
                log_and_print(f"Пауза: {pause_seconds} секунд", 'info')
                time.sleep(pause_seconds)

        log_and_print("Закрытие драйвера...", 'info')
        time.sleep(5)
        driver.quit()