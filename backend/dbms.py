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
        pw_hash, salt = self._hash_new_password(password)
        # generate customer id artificial key
        customer_id = self._new_customer_id()
        # insert customer data into db
        self.cursor.execute(            
            "INSERT INTO CustomerUser (Customer_ID, Username, Email, Phone_Number, Password) VALUES (?, ?, ?, ?, ?)", 
            (customer_id, username, email, phone_number, pw_hash)
            )
        self.connection.commit()
        return True

    def admin_account_creation(self, username: str, password: str) -> bool:
        """ Insert admin data into db if no previous account exists"""
        # don't create account if already exists
        if self._does_admin_exist(username):
            return False
        # hash salted password
        pw_hash, salt = self._hash_new_password(password)
        # generate customer id artificial key
        admin_id = self._new_admin_id()
        # insert customer data into db
        self.cursor.execute(            
            "INSERT INTO AdminUser (Admin_ID, Username, Password) VALUES (?, ?, ?)", 
            (admin_id, username, pw_hash)
            )
        self.connection.commit()
        return True

    def validate_customer_credentials(self, username: str, password: str):
        """Verifies that customer username and password hash are within the db"""

        # pull pw and salt from db for the username
        self.cursor.execute("SELECT Password FROM CustomerUser where Username = ?", (username,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        # verify password hash
        password_hash = res[0]
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def validate_admin_credentials(self, username: str, password: str):
        """Verifies that admin username and password hash are within the db"""
        # pull pw and salt from db for the username
        self.cursor.execute("SELECT Password FROM AdminUser where Username = ?", (username,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        # verify password hash
        password_hash = res[0]
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def _hash_new_password(self, password: str) -> tuple[str, str]:
        """Hashes salted password w/ bcrypt"""
        pw_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(pw_bytes, salt)
        return pw_hash.decode('utf-8'), salt.decode('utf-8')

    def _hash_password_with_previous_salt(self, password: str, salt: bytes) -> bytes:
        """Hashes salted password using a previous salt w/ bcrypt"""
        pw_bytes = password.encode('utf-8')
        return bcrypt.hashpw(pw_bytes, salt)
        
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



