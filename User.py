class User:
    def __init__(self, id, key):
        self.__id = id
        self.__key = key

    def get_id(self):
        return self.__id

    def get_key(self):
        return self.__key

    def set_id(self, id):
        self.__id = id

    def set_key(self, key):
        self.__key = key

    def check_key(self):
        return type(self.__key) == str

