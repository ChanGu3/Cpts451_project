import sqlite3
import bcrypt


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
        """On class destruction, close connection to db"""
        self.connection.close()
        print("Connection to database terminated...")


    def _new_customer_id(self):
        """generate new customer id artifical key"""
        self.cursor.execute("SELECT MAX(Customer_ID) FROM CustomerUser")
        max_customer_id = self.cursor.fetchone()[0]
        if max_customer_id is None:
            return 0
        return max_customer_id + 1


if __name__ == "__main__":
    db = Database("../database/database.db")

    # db.customer_account_creation("test", "test", "test@test.com", "1234567890")