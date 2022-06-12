import gspread
from User import User
from Info import Info
from PasswordCipher import PasswordCipher

gc = gspread.service_account(filename="for-work-with-python-447d976bc7e4.json")

ROWS_NUMBER = "rows_number"
KEY_HASH = "key_hash"

class Table:

    def __init__(self, name):
        self.common_repo = gc.open(name)
        self.repo = self.common_repo.sheet1
        self.rows_number_cell = self.repo.cell(1, 4)
        self.rows_number = 0
        self.key_hash_cell = self.repo.cell(2, 4)
        self.key_hash = "no hash"

    def set_repo(self, user):
        id = user.get_id()
        title = str(id)
        all_titles = list(map(lambda x: x.title, self.common_repo.worksheets()))
        if title in all_titles:
            self.repo = self.common_repo.worksheet(title)
        else:
            self.repo = self.common_repo.add_worksheet(title, 1000, 4)
            self.repo.update_cell(1, 3, ROWS_NUMBER)
            self.repo.update_cell(2, 3, KEY_HASH)
            self.repo.update_cell(1, 4, 0)

        self.set_rows_number_cell()
        self.set_key_hash_cell()

    def set_rows_number_cell(self):
        self.rows_number_cell = self.get_rows_number_cell()
        self.rows_number = int(self.rows_number_cell.value)

    def set_key_hash_cell(self):
        self.key_hash_cell = self.get_key_hash_cell()
        self.key_hash = self.key_hash_cell.value

    def get_rows_number_cell(self):
        rows_number_cell = self.repo.cell(1, 4)
        return rows_number_cell

    def get_key_hash_cell(self):
        key_hash_cell = self.repo.cell(2, 4)
        return key_hash_cell

    def update_rows_number_cell(self):
        self.repo.update_cell(self.rows_number_cell.row, self.rows_number_cell.col, self.rows_number)

    def update_key_hash_cell(self):
        self.repo.update_cell(self.key_hash_cell.row, self.key_hash_cell.col, self.key_hash)

    def empty(self, user):
        self.set_repo(user)
        return self.rows_number == 0

    def check_no_key(self, user):
        self.set_repo(user)
        return self.key_hash is None

    def check_user_key(self, user):
        self.set_repo(user)
        if self.key_hash is None:
            return True

        cipher = PasswordCipher(user)
        return cipher.get_cipher_key_hash() == bytes(self.key_hash, "utf-8")

    @staticmethod
    def is_reserved(name):
        return name == ROWS_NUMBER or name == KEY_HASH

    def add_key(self, user):
        self.set_repo(user)
        cipher = PasswordCipher(user)
        self.key_hash = cipher.get_cipher_key_hash().decode("utf-8")
        self.update_key_hash_cell()

    def change_key(self, user, new_user):
        self.set_repo(new_user)

        cipher = PasswordCipher(user)
        new_cipher = PasswordCipher(new_user)

        self.key_hash = new_cipher.get_cipher_key_hash().decode("utf-8")
        self.update_key_hash_cell()

        for row in range(1, self.rows_number + 1):
            password_cell = self.repo.cell(row, 2)
            encrypted_password = password_cell.value
            password = cipher.decrypt_password(encrypted_password)
            encrypted_password = new_cipher.encrypt_password(password)
            self.repo.update_cell(row, 2, encrypted_password)

        return "Ok, secret key has been successfully changed."

    def get_all_sites(self, user):
        self.set_repo(user)
        sites_list = []
        for row in range(1, self.rows_number + 1):
            site_cell = self.repo.cell(row, 1)
            site = site_cell.value
            sites_list.append(site)

        sites_list.sort()

        result = "Your websites:\n"
        for site in sites_list:
            result += "-> " + site + "\n"
        return result

    def add(self, user, info):
        self.set_repo(user)
        site = info.get_site()
        password = info.get_password()

        if self.is_reserved(site):
            return "Sorry, this name is reserved by me. Please, use another one."

        cell = self.repo.find(site)
        if cell is not None:
            return "You already have the password for this site. Choose 'update' button instead."

        if self.rows_number + 1 > self.repo.row_count:
            return "Sorry, you have exceeded the limit on the number of sites."

        cipher = PasswordCipher(user)
        encrypted_password = cipher.encrypt_password(password)

        self.rows_number += 1
        current_row = self.rows_number
        self.update_rows_number_cell()
        self.repo.update_cell(current_row, 1, site)
        self.repo.update_cell(current_row, 2, encrypted_password)
        return "Ok, new info has been successfully saved."

    def update(self, user, info):
        self.set_repo(user)
        site = info.get_site()
        password = info.get_password()

        site_cell = self.repo.find(site)
        if site_cell is None:
            return "Sorry, this site has not been found. Choose 'add' button instead."

        cipher = PasswordCipher(user)
        encrypted_password = cipher.encrypt_password(password)

        password_cell = self.repo.cell(site_cell.row, site_cell.col + 1)
        self.repo.update_cell(password_cell.row, password_cell.col, encrypted_password)
        return "Ok, password has been successfully updated."

    def get(self, user, info):
        self.set_repo(user)
        site = info.get_site()

        site_cell = self.repo.find(site)
        if site_cell is None:
            return "Sorry, this site has not been found."

        password_cell = self.repo.cell(site_cell.row, site_cell.col + 1)
        encrypted_password = password_cell.value

        cipher = PasswordCipher(user)
        password = cipher.decrypt_password(encrypted_password)

        return "Your password for site " + site + " is " + password

    def delete(self, user, info):
        self.set_repo(user)
        site = info.get_site()

        site_cell = self.repo.find(site)
        if site_cell is None:
            return "Sorry, this site has not been found."

        last_row = self.rows_number
        last_site = self.repo.cell(last_row, 1).value
        last_password = self.repo.cell(last_row, 2).value

        current_row = site_cell.row
        self.repo.update_cell(current_row, 1, last_site)
        self.repo.update_cell(current_row, 2, last_password)

        self.delete_last()

        return "The website " + site + " has been successfully deleted"


    def delete_last(self):
        range = 'A' + str(self.rows_number) + ':B' + str(self.rows_number)
        self.repo.batch_clear([range])
        self.rows_number -= 1
        self.update_rows_number_cell()

