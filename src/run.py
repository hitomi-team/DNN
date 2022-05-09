import asyncio

from bot import DNN


async def start_bot():
    bot = DNN()
    await bot.start()


def main():
    asyncio.run(start_bot())

if __name__ == "__main__":
    main()
