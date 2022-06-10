import gspread
from User import User
from Info import Info

gc = gspread.service_account(filename="for-work-with-python-447d976bc7e4.json")

class Table:

    def __init__(self, name):
        self.common_repo = gc.open(name)
        self.repo = self.common_repo.sheet1

    def set_repo(self, user):
        id = user.get_id()
        title = str(id)
        all_titles = list(map(lambda x: x.title, self.common_repo.worksheets()))
        if title in all_titles:
            self.repo = self.common_repo.worksheet(title)
        else:
            self.repo = self.common_repo.add_worksheet(title, 1000, 4)
            self.repo.update_cell(1, 1, "Website")
            self.repo.update_cell(1, 2, "Password")
            self.repo.update_cell(1, 3, "rows_number")
            self.repo.update_cell(1, 4, 1)

        self.set_rows_number()

    def set_rows_number(self):
        self.rows_number_cell = self.get_rows_number_cell()
        self.rows_number = int(self.rows_number_cell.value)

    def get_rows_number_cell(self):
        rows_number_cell = self.repo.find("rows_number")
        rows_number_cell = self.repo.cell(rows_number_cell.row, rows_number_cell.col + 1)
        return rows_number_cell

    def update_rows_number_cell(self):
        self.repo.update_cell(self.rows_number_cell.row, self.rows_number_cell.col, self.rows_number)

    def add(self, user, info):
        self.set_repo(user)
        site = info.get_site()
        password = info.get_password()

        # TO DO ENCRYPTING

        cell = self.repo.find(site)
        if cell is not None:
            return "You already have the password for this site. Choose 'update' button instead."

        if self.rows_number + 1 > self.repo.row_count:
            return "Sorry, you have exceeded the limit on the number of sites."

        self.rows_number += 1
        current_row = self.rows_number
        self.update_rows_number_cell()
        self.repo.update_cell(current_row, 1, site)
        self.repo.update_cell(current_row, 2, password)
        return "Ok, new info has been successfully saved."

    def update(self, user, info):
        self.set_repo(user)
        site = info.get_site()
        password = info.get_password()

        #TO DO ENCRYPTING

        site_cell = self.repo.find(site)
        if site_cell is None:
            return "Sorry, this site has not been found. Choose 'add' button instead."

        password_cell = self.repo.cell(site_cell.row, site_cell.col + 1)
        self.repo.update_cell(password_cell.row, password_cell.col, password)
        return "Ok, password has been successfully updated."

    def get(self, user, info):
        self.set_repo(user)
        site = info.get_site()

        site_cell = self.repo.find(site)
        if site_cell is None:
            return "Sorry, this site has not been found."

        password_cell = self.repo.cell(site_cell.row, site_cell.col + 1)
        password = password_cell.value

        # TO DO DECRYPTING

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
