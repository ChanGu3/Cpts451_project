import sqlite3
import bcrypt

class Database:
    """
    This class is used to interact with the database file stored in database/database.db
    """

    def __init__(self, database_fname: str):
        self.database_fname = database_fname
        self.connection = sqlite3.connect(self.database_fname)
        print("Connection to database established...")
        self.cursor = self.connection.cursor()
        print("Cursor created...")

    def __del__(self):
        """On class destruction, close connection to db"""
        self.connection.close()
        print("Connection to database terminated...")

    def customer_account_creation(self, username: str, password: str, email: str, phone_number: str) -> bool:
        """ Insert customer data into db if no previous account exists"""
        # don't create account if already exists
        if self._does_customer_username_exist(username):
            return False
        # hash salted password
        pw_hash, salt = self._hash_new_password(password)
        print(pw_hash)
        print(salt)
        # generate customer id artificial key
        customer_id = self._new_customer_id()
        # insert customer data into db
        self.cursor.execute(            
            "INSERT INTO CustomerUser (Customer_ID, Username, Email, Phone_Number, Password) VALUES (?, ?, ?, ?, ?)", 
            (customer_id, username, email, phone_number, pw_hash)
            )
        self.connection.commit()
        return True

    def admin_account_creation(self, username: str, password: str, email: str) -> bool:
        """ Insert admin data into db if no previous account exists"""
        # don't create account if already exists
        if self._does_admin_username_exist(username):
            return False
        # hash salted password
        pw_hash, salt = self._hash_new_password(password)
        print(pw_hash)
        print(salt)
        # generate customer id artificial key
        admin_id = self._new_admin_id()
        # insert customer data into db
        self.cursor.execute(            
            "INSERT INTO AdminUser (Admin_ID, Username, Email, Password) VALUES (?, ?, ?, ?)", 
            (admin_id, username, email, pw_hash)
            )
        self.connection.commit()
        return True

    def validate_customer_username_password(self, username: str, password: str):
        """Verifies that customer username and password hash are within the db"""
        # pull pw and salt from db for the username
        self.cursor.execute("SELECT Password FROM CustomerUser where Username = ?", (username,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        # verify password hash
        password_hash = res[0]
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def validate_customer_id_password(self, customer_id: int, password: str):
        """Verifies that customer id and password hash are within the db"""
        self.cursor.execute("SELECT Password FROM CustomerUser where Customer_ID = ?", (customer_id,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), res[0].encode('utf-8'))

    def validate_admin_username_password(self, username: str, password: str):
        """Verifies that admin username and password hash are within the db"""
        # pull pw and salt from db for the username
        self.cursor.execute("SELECT Password FROM AdminUser where Username = ?", (username,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        # verify password hash
        password_hash = res[0]
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def validate_admin_id_password(self, admin_id: int, password: str):
        """Verifies that admin id and password hash are within the db"""
        self.cursor.execute("SELECT Password FROM AdminUser where Admin_ID = ?", (admin_id,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), res[0].encode('utf-8'))

    def sign_in(self, username: str, password: str):
        """Signs in customer or admin and returns their user id and email"""
        if self.validate_customer_username_password(username, password):
            self.cursor.execute("SELECT Customer_ID, Email FROM CustomerUser WHERE Username = ?", (username,))
            return self.cursor.fetchone()
        elif self.validate_admin_username_password(username, password):
            self.cursor.execute("SELECT Admin_ID, Email FROM AdminUser WHERE Username = ?", (username,))
            return self.cursor.fetchone()

        return None

    def insert_new_product(self, product_details: dict) -> bool:
        """Inserts all product details into the db. Expects all fields to be provided."""

        # create new product id if none provided 
        product_id = product_details["product_id"]
        if product_id is None or not self._does_product_exist(product_id): 
            product_id = self._new_product_id()

        # insert into db
        self.cursor.execute(
            """
            INSERT INTO Product 
            (Product_ID, Title, Price, Stock, Description, DiscountPercentage, WebsiteInfo, DateCreated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            , (
                product_id, 
                product_details["title"], 
                product_details["price"], 
                product_details["stock"], 
                product_details["description"], 
                product_details["discount_percentage"], 
                product_details["website_info"], 
                product_details["date_created"]
                )
        )
        self.connection.commit()
        return True

    def insert_new_product_return_id(self, product_details: dict) -> int:
        """Inserts all product details into the db. Expects all fields to be provided. Gives back the product id of the inserted product."""

        # create new product id if none provided 
        product_id = product_details.get("product_id")
        if product_id is None or not self._does_product_exist(product_id): 
            product_id = self._new_product_id()

        # insert into db
        self.cursor.execute(
            """
            INSERT INTO Product 
            (Product_ID, Title, Price, Stock, Description, DiscountPercentage, WebsiteInfo, DateCreated)
            VALUES (?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%d', 'now'))
            """
            , (
                product_id, 
                product_details["Title"], 
                product_details["Price"], 
                product_details["Stock"], 
                product_details["Description"], 
                product_details["DiscountPercentage"], 
                product_details["WebsiteInfo"]
                )
        )
        self.connection.commit()
        return product_id

    def insert_new_product_image(self, product_id: int, image_name: str, image_data: bytes) -> bool:
        """Inserts product image details into the db. Expects all fields to be provided."""
        if product_id is None or not self._does_product_exist(product_id): 
            return False
        
        self.cursor.execute(
            """
            INSERT INTO ProductImages 
            (Product_ID, ImageName, ImageData)
            VALUES (?, ?, ?)
            """
            , (product_id, image_name, image_data)
        )
        self.connection.commit()
        return True
    
    def insert_new_product_thumbnail(self, product_id: int, image_name: str, image_data: bytes) -> bool:
        """Inserts product thumbnail details into the db. Expects all fields to be provided."""
        if product_id is None or not self._does_product_exist(product_id): 
            return False
        
        if self._does_product_thumbnail_exist(product_id):
            self.cursor.execute(
                """
                UPDATE ProductThumbnail 
                SET ImageName = ?, ImageData = ?
                WHERE Product_ID = ?
                """
                , (image_name, image_data, product_id)
            )
        else:
            self.cursor.execute(
                """
                INSERT INTO ProductThumbnail
                (Product_ID, ImageName, ImageData)
                VALUES (?, ?, ?)
                """
                , (product_id, image_name, image_data)
            )
        
        self.connection.commit()
        return True
        

    def admin_add_product(self, admin_id: int, admin_password: str, product_details: dict) -> bool:
        """Add a new product to the db after validating admin credentials"""
        if self.validate_admin_id_password(admin_id, admin_password):
            self.insert_new_product(product_details)
            return True
        return False
        
    def admin_remove_product(self, admin_id: int, admin_password: str, product_id: int) -> bool:
        """Upon validation of admin credentials, remove a product from the db"""
        if self.validate_admin_id_password(admin_id, admin_password):
            self.cursor.execute("DELETE FROM Product WHERE Product_ID = ?", (product_id,))
            self.connection.commit()
            return True
        return False

    def admin_remove_product_WithOutAdmin(self, product_id: int) -> bool:
        """Upon validation of admin credentials, remove a product from the db"""
        if product_id is None or not self._does_product_exist(product_id): 
            return False
        
        self.cursor.execute("DELETE FROM Product WHERE Product_ID = ?", (product_id,))
        self.connection.commit()
        return True


    def admin_update_product(self, product_id: int, new_product_details: dict) -> bool:
        """Upon validation of admin credentials, update specific columns of a particular product"""
        product_exists = self._does_product_exist(product_id)

        if product_exists:
            update_cols = ', '.join([f"{k} = ?" for k in new_product_details.keys()])
            update_vals = tuple(new_product_details.values())
            self.cursor.execute(f"UPDATE Product SET {update_cols} WHERE Product_ID = ?", update_vals + (product_id,))
            self.connection.commit()
            return True
    
        return False

    def retrieve_all_product_details(self):
        """Gets all product details from the db"""
        self.cursor.execute("SELECT * FROM Product")
        return self.cursor.fetchall()

    def retrieve_all_product_details_With_Thumbnail_With_Analytics(self):
        """Gets all product details from the db"""
        self.cursor.execute("SELECT Product.*, ProductThumbnail.ImageName, sum(ProductsInOrder.Quantity), sum(ProductsInOrder.Quantity * ProductsInOrder.PriceSold) FROM Product INNER JOIN ProductThumbnail ON Product.Product_ID = ProductThumbnail.Product_ID LEFT JOIN ProductsInOrder ON Product.Product_ID = ProductsInOrder.Product_ID GROUP BY Product.Product_ID ORDER BY (CURRENT_DATE - Product.DateCreated) ASC")
        return self.cursor.fetchall()

    def retrieve_specific_product_details(self, product_id: int):
        """Gets specific product details from the db"""
        self.cursor.execute("SELECT * FROM Product WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchone()

    def retrieve_specific_product_images_details(self, product_id: int):
        """Gets specific product images details from the db"""
        self.cursor.execute("SELECT * FROM ProductImages WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchall()

    def retrieve_specific_product_thumbnail_details(self, product_id: int):
        """Gets specific product thumbnail details from the db"""
        self.cursor.execute("SELECT * FROM ProductThumbnail WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchone()

    def get_specific_product_thumbnail(self, productName: int, imageName: str):
        """Gets specific product thumbnail from the db"""
        self.cursor.execute("SELECT ProductThumbnail.ImageData FROM Product inner join ProductThumbnail on Product.product_id = ProductThumbnail.product_id WHERE Product.title = ? AND ProductThumbnail.ImageName = ?", (productName, imageName))
        return self.cursor.fetchone()

    def get_specific_product_image(self, productName: int, imageName: str):
        """Gets specific product image from the db"""
        self.cursor.execute("SELECT ProductImages.ImageData FROM Product inner join ProductImages on Product.product_id = ProductImages.product_id WHERE Product.title = ? AND ProductImages.ImageName = ?", (productName, imageName))
        return self.cursor.fetchone()

    def retrieve_Top_10_product_details(self):
        """Gets top 10 product details from the db"""
        self.cursor.execute("SELECT Product.product_id, Product.title, ProductThumbnail.ImageName, sum(ProductsInOrder.Quantity), sum(ProductsInOrder.pricesold * ProductsInOrder.Quantity) FROM ProductsInOrder INNER JOIN Product on Product.product_id = ProductsInOrder.product_id LEFT JOIN ProductThumbnail on ProductThumbnail.product_id = ProductsInOrder.product_id GROUP BY Product.product_id ORDER BY sum(ProductsInOrder.Quantity) DESC LIMIT 10")
        return self.cursor.fetchall()

    def add_product_category(self, category_name: str) -> bool:
        """Add a new product category to the ProductCategories table"""
        self.cursor.execute("INSERT INTO ProductCategories (CategoryName) VALUES (?)", (category_name,))
        self.connection.commit()
        return True

    def get_all_product_categories(self):
        """Get all product categories from the db"""
        self.cursor.execute("SELECT * FROM ProductCategories")
        return self.cursor.fetchall()

    def set_product_category(self, product_id: int, category_name: str) -> bool:
        """Set a product's category to a pre-existing category in the ProductCategories table"""
        self.cursor.execute("INSERT INTO ProductCategory (Product_ID, CategoryName) VALUES (?, ?)", (product_id, category_name))
        self.connection.commit()
        return True

    def set_product_category_OnlyOne(self, product_id: int, category_name: str) -> bool:
        """Set a product's category to a pre-existing category in the ProductCategories table"""
        if self.cursor.execute("SELECT COUNT(*) FROM ProductCategory WHERE Product_ID = ?", (product_id,)).fetchone()[0] > 0:
            # If there is already a category for this product, remove it before inserting the new one
            self.cursor.execute("DELETE FROM ProductCategory WHERE Product_ID = ?", (product_id,))
        
        self.cursor.execute("INSERT INTO ProductCategory (Product_ID, CategoryName) VALUES (?, ?)", (product_id, category_name))
        self.connection.commit()
        return True

    def update_product_category(self, product_id: int, category_name: str) -> bool:
        """Updates pre-existing product category in db"""
        self.cursor.execute("UPDATE ProductCategory SET CategoryName = ? WHERE Product_ID = ?", (category_name, product_id))
        self.connection.commit()
        return True

    def get_product_category(self, product_id: int):
        """Get all product categories for a given product from the db"""
        self.cursor.execute("SELECT CategoryName FROM ProductCategory WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchone()

    def search_products_by_category(self, category_name: str):
        """ gets all product details with a given category name"""
        self.cursor.execute(
            """
            SELECT * FROM Product 
            WHERE Product_ID IN (
                SELECT Product_ID FROM ProductCategory 
                WHERE CategoryName = ?
            )
            """, 
            (category_name,)
            )
        return self.cursor.fetchall()

    def search_products_by_name(self, product_name: str):
        """gets all product details with a given product name """
        self.cursor.execute("SELECT * FROM Product WHERE Title = ?", (product_name,))
        return self.cursor.fetchall()

    def search_products_by_name_With_Thumbnail_With_Analytics(self, product_name: str):
        """gets all product details with a given product name """
        self.cursor.execute("SELECT Product.*, ProductThumbnail.ImageName FROM Product INNER JOIN ProductThumbnail ON Product.Product_ID = ProductThumbnail.Product_ID LEFT JOIN ProductsInOrder ON Product.Product_ID = ProductsInOrder.Product_ID WHERE Product.Title LIKE ? GROUP BY Product.Product_ID ORDER BY (CURRENT_DATE - Product.DateCreated) ASC;", ('%' + product_name + '%',))
        return self.cursor.fetchall()

    def search_product_by_id(self, product_id: int):
        """gets the product details for a given product id"""
        self.cursor.execute("SELECT * FROM Product WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchone()

    def get_customer_info(self, customer_id: int):
        """gets customer info from db"""
        self.cursor.execute("SELECT * FROM CustomerUser WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchone()

    def get_admin_info(self, admin_id: int):
        """gets admin info from db"""
        self.cursor.execute("SELECT * FROM AdminUser WHERE Admin_ID = ?", (admin_id,))
        return self.cursor.fetchone()

    def update_customer_password(self, username: str, old_password: str, new_password: str):
        """Update customer password if old password is correct"""
        if self.validate_customer_username_password(username, old_password):
            pw_hash, salt = self._hash_new_password(new_password)
            self.cursor.execute("UPDATE CustomerUser SET Password = ? WHERE Username = ?", (pw_hash, username))
            self.connection.commit()
            return True
        return False

    def update_admin_password(self, username: str, old_password: str, new_password: str):
        """Update admin password if old password is correct"""
        if self.validate_admin_username_password(username, old_password):
            pw_hash, salt = self._hash_new_password(new_password)
            self.cursor.execute("UPDATE AdminUser SET Password = ? WHERE Username = ?", (pw_hash, username))
            self.connection.commit()
            return True
        return False

    def update_customer_email(self, customer_id: int, password: str, new_email: str) -> bool:
        """Updates customer email upon user credential validation"""
        if self.validate_customer_id_password(customer_id, password):
            self.cursor.execute("UPDATE CustomerUser SET Email = ? WHERE Customer_ID = ?", (new_email, customer_id))
            self.connection.commit()
            return True
        return False

    def update_admin_email(self, admin_id: int, password: str, new_email: str) -> bool:
        """Updates admin email upon user credential validation"""
        if self.validate_admin_id_password(admin_id, password):
            self.cursor.execute("UPDATE AdminUser SET Email = ? WHERE Admin_ID = ?", (new_email, admin_id))
            self.connection.commit()
            return True
        return False

    def add_product_to_wishlist(self, customer_id: int, product_id: int) -> bool:
        """Inserts a pre-existing product into the customer's wishlist"""
        customer_exists = self._does_customer_id_exist(customer_id)
        product_exists = self._does_product_exist(product_id)
        if customer_exists and product_exists:
            self.cursor.execute("INSERT INTO Wishlist (Customer_ID, Product_ID) VALUES (?, ?)", (customer_id, product_id))
            self.connection.commit()
            return True
        return False

    def remove_product_from_wishlist(self, customer_id: int, product_id: int) -> bool:
        """Removes the specified product id from the customer's wishlist"""
        self.cursor.execute("DELETE FROM Wishlist WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id))
        self.connection.commit()
        return True

    def get_all_wishlist_product_ids(self, customer_id: int):
        """
        Returns the product ids of all products in the wishlist. 
        search_product_by_id() can then be used to get the details.
        """
        self.cursor.execute("SELECT Product_ID FROM Wishlist WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchall()

    def add_product_to_cart(self, customer_id: int, product_id: int, quantity: int) -> bool:
        customer_exists = self._does_customer_id_exist(customer_id)
        product_exists = self._does_product_exist(product_id)
        if customer_exists and product_exists:
            if self._does_Cart_Product_exist(customer_id, product_id):
                # If the product is already in the cart, update the quantity
                self.cursor.execute("UPDATE Cart SET Quantity = Quantity + ? WHERE Customer_ID = ? AND Product_ID = ?", (quantity, customer_id, product_id))
            else:
                self.cursor.execute("INSERT INTO Cart (Customer_ID, Product_ID, Quantity) VALUES (?, ?, ?)", (customer_id, product_id, quantity))
            self.connection.commit()
            return True
        return False

    def remove_product_from_cart(self, customer_id: int, product_id: int, quantity: int) -> bool:
        """Removes a product from the customer's cart"""
        customer_exists = self._does_customer_id_exist(customer_id)
        product_exists = self._does_product_exist(product_id)
        if customer_exists and product_exists:
            product_info = self._does_Cart_Product_exist(customer_id, product_id)
            if product_info is not None:
                if product_info[2] > quantity:
                    # If the quantity is greater than the quantity to remove, update the quantity
                    self.cursor.execute("UPDATE Cart SET Quantity = Quantity - ? WHERE Customer_ID = ? AND Product_ID = ?", (quantity, customer_id, product_id))
                else:
                    self.cursor.execute("DELETE FROM Cart WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id))
                self.connection.commit()
                return True
        return False

    def get_all_product_ids_and_quantity_in_cart(self, customer_id: int):
        """
        Returns the product ids of all products in the cart. 
        search_product_by_id() can then be used to get the details.
        """
        self.cursor.execute("SELECT Product_ID, Quantity FROM Cart WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchall()

    def add_new_order(self, customer_id: int):
        pass

    def get_order_details(self, order_id: int):
        pass

    def remove_order(self, order_id: int):
        pass

    def update_order_status(self, admin_id: int, order_id: int):
        pass

    def get_all_orders_from_user(self, customer_id: int):
        pass


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
        
    def _does_customer_username_exist(self, username: str) -> bool:
        """Checks if there is a customer in the db with this username"""
        self.cursor.execute("SELECT Username FROM CustomerUser WHERE Username = ?", (username,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _does_customer_id_exist(self, customer_id: int) -> bool:
        """Checks if there is a customer in the db with this id"""
        self.cursor.execute("SELECT Customer_ID FROM CustomerUser WHERE Customer_ID = ?", (customer_id,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _does_admin_username_exist(self, username: str) -> bool:
        """Checks if there is an admin in the db with this username"""
        self.cursor.execute("SELECT Username FROM AdminUser WHERE Username = ?", (username,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _does_product_exist(self, product_id: int) -> bool:
        """Checks if product exists in db"""
        self.cursor.execute("SELECT Product_ID FROM Product WHERE Product_ID = ?", (product_id,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _does_product_thumbnail_exist(self, product_id: int) -> bool:
        """Checks if product thumbnail exists in db"""
        self.cursor.execute("SELECT Product_ID FROM ProductThumbnail WHERE Product_ID = ?", (product_id,))
        if len(self.cursor.fetchall()) == 0:
            return False
        return True

    def _does_Cart_Product_exist(self, customer_id: int, product_id: int) -> bool:
        """Checks if product is in the cart for the customer"""
        self.cursor.execute("SELECT Customer_ID, Product_ID, Quantity FROM Cart WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id,))
        data = len(self.cursor.fetchall())
        if len(data) == 0:
            return data
        return None

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

    def _new_product_id(self) -> int:
        """generate new product id artifical key"""
        self.cursor.execute("SELECT MAX(Product_ID) FROM Product")
        max_product_id = self.cursor.fetchone()[0]
        if max_product_id is None:
            return 0
        return max_product_id + 1
