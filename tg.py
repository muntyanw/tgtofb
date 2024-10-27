from telethon import TelegramClient, events
from browser_utils import sendOneMessagessToFb
from log import log_and_print  # Импорт функции логирования

# Глобальный флаг для предотвращения двойной реакции
processed_messages = set()

async def startTgClient(tg_creds, fb_creds, fb_groups, tg_channels):
    channels = tg_channels.get('channels', [])
    if not channels:
        log_and_print("Список каналов пуст.", 'warning')
        return

    channel_data = channels[0]
    telegram_channel_name = channel_data.get('telegram_channel_name')
    bot_token = tg_creds.get('bot_token')
    api_id = tg_creds.get('api_id')
    api_hash = tg_creds.get('api_hash')

    if not (telegram_channel_name and bot_token and api_id and api_hash):
        log_and_print("Недостаточно данных для подключения к Telegram.", 'error')
        return

    # Создаем клиент Telethon
    bot_client = TelegramClient('bot_session', api_id, api_hash)

    try:
        log_and_print(f"Запуск клиента с токеном: {bot_token}", 'info')
        await bot_client.start(bot_token=bot_token)
        log_and_print("Клиент успешно запущен.", 'info')

        @bot_client.on(events.NewMessage)
        async def handler(event):
            message_id = event.message.id
            if message_id in processed_messages:
                # Сообщение уже обработано
                return

            # Добавляем ID сообщения в список обработанных
            processed_messages.add(message_id)

            message_text = event.message.message
            log_and_print(f'Получено новое сообщение из Telegram: {message_text}', 'info')
            sendOneMessagessToFb(message_text, fb_creds, fb_groups)

        # Получаем объект канала
        try:
            telegram_channel_entity = await bot_client.get_entity(telegram_channel_name)
            telegram_channel_id = telegram_channel_entity.id
            log_and_print(f"Подключение к каналу: @{telegram_channel_name} (ID: {telegram_channel_id})", 'info')
        except Exception as e:
            log_and_print(f"Ошибка получения информации о канале: {e}", 'error')
            return

        # Устанавливаем обработчик для сообщений в этом канале
        bot_client.add_event_handler(handler, events.NewMessage(chats=telegram_channel_id))

        log_and_print('Начинаем прослушивание канала Telegram...', 'info')
        await bot_client.run_until_disconnected()

    except Exception as e:
        log_and_print(f"Ошибка при запуске клиента: {e}", 'error')
