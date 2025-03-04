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

    def customer_account_creation(self, username: str, password: str, email: str, phone_number: str) -> bool:
        """ Insert customer data into db if no previous account exists"""
        # don't create account if already exists
        if self._does_customer_exist(username):
            return False
        # hash salted password
        pw_hash, salt = self._hash_password(password)
        # generate customer id artificial key
        customer_id = self._new_customer_id()
        # insert customer data into db
        self.cursor.execute(            
            "INSERT INTO CustomerUser (Customer_ID, Username, Email, Phone_Number, Password, Salt) VALUES (?, ?, ?, ?, ?, ?)", 
            (customer_id, username, email, phone_number, pw_hash, salt)
            )
        self.connection.commit()
        return True

    def admin_account_creation(self, username: str, password: str) -> bool:
        """ Insert admin data into db if no previous account exists"""
        # don't create account if already exists
        if self._does_admin_exist(username):
            return False
        # hash salted password
        pw_hash, salt = self._hash_password(password)
        # generate customer id artificial key
        admin_id = self._new_admin_id()
        # insert customer data into db
        self.cursor.execute(            
            "INSERT INTO AdminUser (Admin_ID, Username, Password, Salt) VALUES (?, ?, ?, ?)", 
            (admin_id, username, pw_hash, salt)
            )
        self.connection.commit()
        return True

    def _hash_password(self, password: str) -> tuple[bytes, bytes]:
        """Hashes salted password w/ bcrypt"""
        pw_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(pw_bytes, salt)
        return pw_hash, salt
        
    def _does_customer_exist(self, username: str) -> bool:
        """Checks if customer exists in db """
        self.cursor.execute("SELECT Username FROM CustomerUser WHERE Username = ?", (username,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _does_admin_exist(self, username: str) -> bool:
        """Checks if admin exists in db"""
        self.cursor.execute("SELECT Username FROM AdminUser WHERE Username = ?", (username,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _new_customer_id(self) -> int:
        """generate new customer id artifical key"""
        self.cursor.execute("SELECT MAX(Customer_ID) FROM CustomerUser")
        max_customer_id = self.cursor.fetchone()[0]
        if max_customer_id is None:
            return 0
        return max_customer_id + 1

    def _new_admin_id(self) -> int:
        """generate new admin id artifical key"""
        self.cursor.execute("SELECT MAX(Admin_ID) FROM AdminUser")
        max_admin_id = self.cursor.fetchone()[0]
        if max_admin_id is None:
            return 0
        return max_admin_id + 1



