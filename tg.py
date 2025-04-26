from telethon import TelegramClient, events
from browser_utils import sendOneMessagessToFb
from log import log_and_print  # Импорт функции логирования
import asyncio
from telethon.errors import RPCError
from telethon import TelegramClient

# Глобальный флаг для предотвращения двойной реакции
processed_messages = set()
# Семафор для последовательной обработки сообщений
processing_semaphore = asyncio.Semaphore(1)

telegram_channel_name = None
telegram_channel_id = None

async def send_message_to_tg_channel(bot_client, channel_name, message_text, image_path=None):
    try:
        # Получаем объект канала
        channel_entity = await bot_client.get_entity(channel_name)

        # Отправка сообщения с изображением или только текста
        if image_path:
            await bot_client.send_file(
                channel_entity,
                image_path,
                caption=message_text[:1024]  # Обрезаем подпись до допустимой длины
            )
        else:
            await bot_client.send_message(
                channel_entity,
                message_text
            )

        log_and_print(f"Сообщение успешно отправлено в канал: {channel_name}", 'info')

    except RPCError as e:
        log_and_print(f"Ошибка при отправке сообщения в канал: {e}", 'error')
    except Exception as e:
        log_and_print(f"Непредвиденная ошибка при отправке сообщения в канал: {e}", 'error')

async def process_one_message(event, bot_client, service_channel_name, fb_creds, fb_groups, fone_colors, chromedriver_port, time_wait_login, xpaths):
    chatIdStr = str(event.chat_id)
    needTGChannelId = str(telegram_channel_id)
    needTGChannelId100 = "-100" + needTGChannelId

    if chatIdStr !=needTGChannelId and chatIdStr !=needTGChannelId100:
        log_and_print(f"Повідомлення в канал event.chat_id : {event.chat_id}, event.chat_id = {event.chat_id}, telegram_channel_id = {telegram_channel_id}", 'info')
        entity = await bot_client.get_entity(event.chat_id)
        name = entity.title if hasattr(entity, 'title') else None
        log_and_print(f"Ім'я канала  : {name}", 'info')
        return

    log_and_print(f"Нове повідомлення в канал {telegram_channel_name}", 'info')

    message_id = event.message.id
    if message_id in processed_messages:
        log_and_print(f"Сообщение уже обработано", 'info')
        return

    # Добавляем ID сообщения в список обработанных
    processed_messages.add(message_id)

    message_text = event.message.message
    image_path = None

    # Проверка наличия изображения в сообщении
    if event.message.photo or event.message.file:
        log_and_print("Обнаружено изображение, начинается загрузка...", 'info')

        # Формируем имя файла и загружаем изображение
        file_name = f"downloads/{event.message.id}.jpg"
        image_path = await event.message.download_media(file=file_name)

        if image_path:
            log_and_print(f"Изображение успешно загружено: {image_path}", 'info')
        else:
            log_and_print("Не удалось загрузить изображение.", 'error')

    log_and_print(f'Получено новое сообщение из Telegram: {message_text}', 'info')

    # Обрабатываем сообщение последовательно с использованием семафора
    async with processing_semaphore:
        try:
            log_and_print(f'Обработка сообщения: {message_text}', 'info')

            await send_message_to_tg_channel(bot_client, service_channel_name,
                                             f"Відправляєм повідомлення - {message_text} - цикл по группам почався.")

            sendOneMessagessToFb(message_text, fb_creds, fb_groups, fone_colors, chromedriver_port, time_wait_login, xpaths, image_path=image_path)

            await send_message_to_tg_channel(bot_client, service_channel_name, f"Цикл по групам закінчен.")

        except Exception as e:
            log_and_print(f"Oшибка при обработке одного сообщения: {e}", 'error')
            await asyncio.sleep(10)  # Задержка

async def check_connection(bot_client):
    while True:
        if not bot_client.is_connected():
            try:
                log_and_print("Потеряно подключение. Переподключение...", 'warning')
                await bot_client.connect()
                if bot_client.is_user_authorized():
                    log_and_print("Подключение восстановлено.", 'info')
                else:
                    log_and_print("Авторизация потеряна. Необходимо перезайти.", 'error')
            except Exception as e:
                log_and_print(f"Ошибка при попытке переподключения: {e}", 'error')
        await asyncio.sleep(10)  # Проверяем каждые 10 секунд

async def start_listening(bot_client):
    while True:
        try:
            log_and_print('Начинаем прослушивание канала Telegram...', 'info')
            await bot_client.run_until_disconnected()
        except Exception as e:
            log_and_print(f"Ошибка при прослушивании Telegram: {e}. Переподключение через 5 секунд...", 'error')
            await asyncio.sleep(5)  # Задержка перед повторной попыткой

async def startTgClient(tg_creds, fb_creds, fb_groups, tg_channels, settings):

    global telegram_channel_name
    global telegram_channel_id

    channels = tg_channels.get('channels', [])
    if not channels:
        log_and_print("Список каналов пуст.", 'warning')
        return

    channel_data = channels[0]
    telegram_channel_name = channel_data.get('telegram_channel_name')

    service_channels = tg_channels.get('service_channels', [])
    if not service_channels:
        log_and_print("Список сервісних каналів пуст.", 'warning')
        return

    service_channel_data = service_channels[0]
    service_channel_name = service_channel_data.get('service_channel_name')

    bot_token = tg_creds.get('bot_token')
    api_id = tg_creds.get('api_id')
    api_hash = tg_creds.get('api_hash')

    fone_colors = settings.get('fone_colors')
    chromedriver_port = settings.get('chromedriver_port')
    time_wait_login = settings.get('time_wait_login') or 60
    xpaths = settings.get('xpaths') 

    #sendOneMessagessToFb("", fb_creds, fb_groups, image_path="E:\\ttofb\\downloads\\31.jpg")

    if not (telegram_channel_name and bot_token and api_id and api_hash):
        log_and_print("Недостаточно данных для подключения к Telegram.", 'error')
        return

    # Создаем клиент Telethon
    bot_client = TelegramClient('bot_session', api_id, api_hash)

    while True:
        try:
            log_and_print(f"Запуск клиента с токеном: {bot_token}", 'info')
            await bot_client.start(bot_token=bot_token)
            log_and_print("Клиент успешно запущен.", 'info')

            # Получаем информацию о боте
            bot_info = await bot_client.get_me()

            log_and_print(f"Имя бота: {bot_info.first_name}", 'info')
            log_and_print(f"Юзернейм бота: {bot_info.username}", 'info')

            break  # Выход из цикла, если подключение успешно
        except RPCError as e:
            log_and_print(f"Ошибка подключения к Telegram: {e}. Повторная попытка через 10 секунд...", 'error')
            await asyncio.sleep(10)  # Задержка перед повторной попыткой
        except Exception as e:
            log_and_print(f"Непредвиденная ошибка: {e}. Повторная попытка через 10 секунд...", 'error')
            await asyncio.sleep(10)  # Задержка

    try:
        if not telegram_channel_id:
            telegram_channel_entity = await bot_client.get_entity(telegram_channel_name)
            telegram_channel_id = telegram_channel_entity.id
            log_and_print(f"Подключение к каналу: @{telegram_channel_name} (ID: {telegram_channel_id})", 'info')
    except Exception as e:
        # maybe is id

        log_and_print(f"Ошибка получения информации о канале {telegram_channel_name}: {e}", 'error')
        return

    try:
        @bot_client.on(events.NewMessage)
        async def handler(event):
            await process_one_message(event, bot_client, service_channel_name, fb_creds, fb_groups, fone_colors, chromedriver_port, time_wait_login, xpaths)


        bot_client.add_event_handler(handler, events.NewMessage(chats=telegram_channel_id))

        asyncio.create_task(check_connection(bot_client))

        await start_listening(bot_client)

    except Exception as e:
        log_and_print(f"Ошибка при запуске клиента: {e}", 'error')
