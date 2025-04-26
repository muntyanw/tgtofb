import asyncio
from tg import startTgClient
from init import init

if __name__ == '__main__':
    try:
        import platform
        print(platform.architecture())
        tg_creds, fb_creds, fb_groups, tg_channels, settings = init()
        asyncio.run(startTgClient(tg_creds, fb_creds, fb_groups, tg_channels, settings))
    except RuntimeError as e:
        if "no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(startTgClient())

        input("Press Enter to exit...")
