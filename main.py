from modules.telegram_bot import TelegramBot

if __name__ == '__main__':
    print("Iniciando bot de análise de ações...")
    bot = TelegramBot()
    bot.run()