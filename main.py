import telebot
from Table import Table
from PasswordBot import PasswordBot

bot = telebot.TeleBot("token")
table = Table("name")
mine_bot = PasswordBot(bot, table)
mine_bot.bot_runner()

