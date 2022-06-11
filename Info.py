class Info:
    def __init__(self, site, password):
        self.__site = site
        self.__password = password

    def set_site(self, site):
        self.__site = site

    def set_password(self, password):
        self.__password = password

    def get_site(self):
        return self.__site

    def get_password(self):
        return self.__password

    def check_data(self):
        return type(self.__site) == str and type(self.__password) == str

