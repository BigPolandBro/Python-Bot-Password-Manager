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

    @staticmethod
    def gen_markup_actions():
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Add new password", callback_data="cb_add"),
                   InlineKeyboardButton("Get existing password", callback_data="cb_get"),
                   InlineKeyboardButton("Update password", callback_data="cb_update"),
                   InlineKeyboardButton("Delete password", callback_data="cb_delete"),
                   InlineKeyboardButton("Change secret key", callback_data="cb_change_key"),
                   InlineKeyboardButton("Show all my sites", callback_data="cb_all_sites"))
        return markup

    def process_start_menu(self, message):
        self.__bot.send_message(message.chat.id, "Hello, this is your FREE personal bot for working with your website passwords.\n"
                                                 "I mean, I'm just a password manager.\n"
                                                 "I can store, change, delete, display your passwords.\n"
                                                 "I will keep them encrypted, so don't be afraid that someone will steal them.\n"
                                                 "But for all this, I need a secret key from you.")
        self.process_key_info(message)
        self.process_action_menu(message)

    def process_key_info(self, message):
        self.__bot.send_message(message.chat.id, "ABOUT KEY.\n"
                                                 "You should have the key, that will be used for encoding/decoding your passwords.\n"
                                                 "Once you use it for encryption, you need to remember it forever.\n"
                                                 "Otherwise you will lose access to your passwords, it will be impossible to recover them.\n"
                                                 "You have the possibility to change the key at every moment. It is a good practice for safety.\n"
                                                 "If it is the first time you use this manager, come up with a good key.\n"
                                                 "The key is the password to your passwords. The key must be a string of characters.\n"
                                                 "Your key should be somewhat secure:\n" 
                                                 "--- Do not use very short key!\n"
                                                 "--- Do not use common words and phrases!\n"
                                                 "It is your responsibility to remember your key, I don't keep it anywhere.\n"
                                                 "It should be not only secure, but also memorable.\n"
                                                 "Create key based on phrases that mean something to you, and you will easily remember it.\n"
                                                 "Do not forget you key!\n" 
                                                 "I will ask it every time you want to interact with your passwords or change the key.\n")

    def process_action_menu(self, message):
        self.__bot.send_message(message.chat.id, "Choose what you want to do:",
                                                 reply_markup=self.gen_markup_actions())

    def process_idk(self, message):
        self.__bot.reply_to(message,
                                "I don't get you! Please, use commands:\n"
                                " /start to start bot\n"
                                " /key to view important information about secret key\n"
                                " /actions to view what I can do\n")

    def process_smth_went_wrong(self, message):
        self.__bot.reply_to(message,
                                "Oooooops! Something went wrong. Please, write to @poremido to leave a bug report.")

    def add_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's save it")
        self.process_first_step(call)

    def get_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's get it")
        self.process_first_step(call)

    def update_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's update it")
        self.process_first_step(call)

    def delete_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's delete it")
        self.process_first_step(call)

    def change_key_action(self, call):
        self.__bot.answer_callback_query(call.id, "Let's change key")
        self.process_first_step(call)

    def show_all_sites_action(self, call):
        self.__bot.answer_callback_query(call.id, "Ok, I will show you")
        self.process_first_step(call)

    def process_first_step(self, call):
        user = User(call.message.chat.id, "no key")

        key_status = "current"
        if self.__table.check_no_key(user):
            self.__bot.send_message(call.message.chat.id, "Now I will ask you to enter your first key. Be careful."
                                                          "Nothing is possible without a valid key.")
            key_status = "first"
        key_message = self.__bot.send_message(call.message.chat.id, "Print your " + key_status + " secret key:")
        self.__bot.register_next_step_handler(key_message, self.process_key_step, user, call.data)

    def process_key_step(self, message, user, cb_data):
        key = message.text
        user.set_key(key)

        if not user.check_key():
            self.__bot.send_message(message.chat.id, "You should print only text messages."
                                                     "You may press /key to see more information. Come on again.")
            self.process_action_menu(message)
            return

        first_key = False
        if self.__table.check_no_key(user):
            self.__table.add_key(user)
            self.__bot.send_message(message.chat.id, "Your first key has been successfully added.")
            first_key = True
        else:
            if not self.__table.check_user_key(user):
                self.__bot.send_message(message.chat.id, "You used a different key before."
                                                         "I can't let you do anything until you remember it.\n"
                                                         "Press /key to see more information or /actions to try again.")
                return

        if cb_data == "cb_change_key":
            if first_key:
                self.process_action_menu(message)
            else:
                new_key_message = self.__bot.send_message(message.chat.id, "Print new secret key:")
                self.__bot.register_next_step_handler(new_key_message, self.process_key_change_step, user, cb_data)
            return

        if cb_data == "cb_all_sites":
            try:
                result = self.__table.get_all_sites(user)
                self.__bot.send_message(message.chat.id, result)
            except Exception as e:
                self.process_smth_went_wrong(message)
            self.process_action_menu(message)
            return

        site_message = self.__bot.send_message(message.chat.id, "Print the website:")
        self.__bot.register_next_step_handler(site_message, self.process_site_step, user, cb_data)

    def process_key_change_step(self, message, user, cb_data):
        new_key = message.text
        new_user = User(user.get_id(), new_key)

        #try:
        result = self.__table.change_key(user, new_user)
        self.__bot.send_message(message.chat.id, result)
        #except Exception as e:
            #self.process_smth_went_wrong(message)
        self.process_action_menu(message)
        return

    def process_site_step(self, message, user, cb_data):
        site = message.text
        info = Info(site, site)

        if not info.check_data():
            self.__bot.send_message(message.chat.id, "You should print only text messages. Come on again.")
            self.process_action_menu(message)
            return

        if cb_data == "cb_delete":
            try:
                result = self.__table.delete(user, info)
                self.__bot.send_message(message.chat.id, result)
            except Exception as e:
                self.process_smth_went_wrong(message)
            self.process_action_menu(message)
            return

        if cb_data == "cb_get":
            try:
                result = self.__table.get(user, info)
                self.__bot.send_message(message.chat.id, result)
            except Exception as e:
                self.process_smth_went_wrong(message)
            self.process_action_menu(message)
            return

        password_message = self.__bot.send_message(message.chat.id, "Print password for this site:")
        self.__bot.register_next_step_handler(password_message, self.process_password_step, user, info, cb_data)

    def process_password_step(self, message, user, info, cb_data):
        password = message.text
        info.set_password(password)

        if not info.check_data():
            self.__bot.send_message(message.chat.id, "You should print only text messages. Come on again.")
            self.process_action_menu(message)
            return

        try:
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

        @self.__bot.message_handler(commands=["key"])
        def message_handler_actions(message, res=False):
            self.process_key_info(message)

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
            elif call.data == "cb_change_key":
                self.change_key_action(call)
            elif call.data == "cb_all_sites":
                self.show_all_sites_action(call)

            self.__bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

        self.__bot.polling(none_stop=True, interval=0)
