import sqlite3


class Database:
    """
    This class is used to interact with the database file stored in database/database.db
    """

    def __init__(self, database_fname: str):
        
        self.database_fname = database_fname

        # connect to the database
        self.connection = sqlite3.connect(self.database_fname)
        print("Connection to database established...")

        # create cursor
        self.cursor = self.connection.cursor()
        print("Cursor created...")

    def __del__(self):
        """On class destruction, close connect to db"""
        self.connection.close()
        print("Connection to database terminated...")
        


if __name__ == "__main__":
    db = Database("../database/database.db")