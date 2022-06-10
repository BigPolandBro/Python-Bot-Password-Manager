import telebot

from Table import Table
from Info import Info
from User import User

from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class PasswordBot:
    def __init__(self, bot, table):
        self.__bot = bot
        self.__table = table

    def gen_markup_actions(self):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Add new password", callback_data="cb_add"),
                   InlineKeyboardButton("Get existing password", callback_data="cb_get"),
                   InlineKeyboardButton("Update password", callback_data="cb_update"),
                   InlineKeyboardButton("Delete password", callback_data="cb_delete"))
        return markup

    def process_start_menu(self, message):
        self.__bot.send_message(message.chat.id, "Hello, this is your personal bot for working with "
                                                 "your website passwords. Choose an action from buttons below",
                                                  reply_markup=self.gen_markup_actions())

    def process_action_menu(self, message):
        self.__bot.send_message(message.chat.id, "Choose what you want to do:",
                                                 reply_markup=self.gen_markup_actions())

    def process_idk(self, message):
        self.__bot.reply_to(message,
                                "I don't get you! Please, use command /start to start work or /actions "
                                "to view possible actions.")

    def process_smth_went_wrong(self, message):
        self.__bot.reply_to(message,
                                "Oooooops! Something went wrong. Please, write to @poremido to leave a bug report.")

    def add_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's save it")
        site_message = self.__bot.send_message(call.message.chat.id, "Print the website:")
        self.__bot.register_next_step_handler(site_message, self.process_site_step, call.data)

    def get_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's get it")
        site_message = self.__bot.send_message(call.message.chat.id, "Print the website:")
        self.__bot.register_next_step_handler(site_message, self.process_site_step, call.data)

    def update_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's update it")
        site_message = self.__bot.send_message(call.message.chat.id, "Print the website:")
        self.__bot.register_next_step_handler(site_message, self.process_site_step, call.data)

    def delete_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's delete it")
        site_message = self.__bot.send_message(call.message.chat.id, "Print the website:")
        self.__bot.register_next_step_handler(site_message, self.process_site_step, call.data)

    def process_site_step(self, message, cb_data):
        site = message.text
        info = Info(site, site)

        if cb_data == "cb_delete":
            try:
                user = User(message.chat.id)
                result = self.__table.delete(user, info)
                self.__bot.send_message(message.chat.id, result)
            except Exception as e:
                self.process_smth_went_wrong(message)
            self.process_action_menu(message)
            return

        if cb_data == "cb_get":
            try:
                user = User(message.chat.id)
                result = self.__table.get(user, info)
                self.__bot.send_message(message.chat.id, result)
            except Exception as e:
                self.process_smth_went_wrong(message)
            self.process_action_menu(message)
            return

        password_message = self.__bot.send_message(message.chat.id, "Print password for this site:")
        self.__bot.register_next_step_handler(password_message, self.process_password_step, info, cb_data)

    def process_password_step(self, message, info, cb_data):
        try:
            password = message.text
            info.set_password(password)
            user = User(message.chat.id)

            if cb_data == "cb_add":
                result = self.__table.add(user, info)
                self.__bot.send_message(message.chat.id, result)

            if cb_data == "cb_update":
                result = self.__table.update(user, info)
                self.__bot.send_message(message.chat.id, result)

        except Exception as e:
            self.process_smth_went_wrong(message)

        self.process_action_menu(message)

    def bot_runner(self):
        @self.__bot.message_handler(commands=["start"])
        def message_handler_start(message, res=False):
            self.process_start_menu(message)

        @self.__bot.message_handler(commands=["actions"])
        def message_handler_actions(message, res=False):
            self.process_action_menu(message)

        @self.__bot.message_handler(content_types=["text"])
        def message_handler_other(message):
            self.process_idk(message)

        @self.__bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if call.data == "cb_add":
                self.add_action(call)
            elif call.data == "cb_get":
                self.get_action(call)
            elif call.data == "cb_update":
                self.update_action(call)
            elif call.data == "cb_delete":
                self.delete_action(call)

            self.__bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

        self.__bot.polling(none_stop=True, interval=0)
