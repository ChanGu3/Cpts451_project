import sqlite3
import bcrypt
from enum import Enum
from typing import List, Tuple

class UserType(Enum):
    CUSTOMER = 0
    ADMIN = 1

class Database:
    """
    This class is used to interact with the database file stored in database/database.db
    """

    def __init__(self, database_fname: str):
        self.database_fname = database_fname
        self.connection = sqlite3.connect(self.database_fname)
        self.connection.row_factory = sqlite3.Row
        print("Connection to database established...")
        self.cursor = self.connection.cursor()
        print("Cursor created...")

        self.default_order_status = "Order In Progress"

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
            "INSERT INTO CustomerUser (Customer_ID, Username, Email, Password, Phone_Number) VALUES (?, ?, ?, ?, ?)", 
            (customer_id, username, email, pw_hash, phone_number,)
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
            return self.cursor.fetchone(), UserType.CUSTOMER
        elif self.validate_admin_username_password(username, password):
            self.cursor.execute("SELECT Admin_ID, Email FROM AdminUser WHERE Username = ?", (username,))
            return self.cursor.fetchone(), UserType.ADMIN

        return None, None

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

    def product_stock(self, product_id: int) -> int:
        """Gets the stock of a product from the db"""
        self.cursor.execute("SELECT Stock FROM Product WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchone()[0]

    def product_price(self, product_id: int) -> float:
        """Gets the price of a product from the db"""
        self.cursor.execute("SELECT Price FROM Product WHERE Product_ID = ?", (product_id,))
        return self.cursor.fetchone()[0]

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
        self.cursor.execute("""
        SELECT Product.Product_ID, Product.Title, Product.Price, ProductThumbnail.ImageName
        FROM Product
        LEFT JOIN ProductThumbnail ON Product.Product_ID = ProductThumbnail.Product_ID
        WHERE ProductThumbnail.ImageName IS NOT NULL
        ORDER BY Product.DateCreated DESC
        """)
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
        """Retrieve the top 10 products sorted by stock."""
        self.cursor.execute("""
        SELECT Product.Product_ID, Product.Title, Product.Price, ProductThumbnail.ImageName, Product.Stock
        FROM Product
        LEFT JOIN ProductThumbnail ON Product.Product_ID = ProductThumbnail.Product_ID
        WHERE ProductThumbnail.ImageName IS NOT NULL
        ORDER BY Product.Stock DESC
        LIMIT 10
        """)
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
            if self._does_cart_product_exist(customer_id, product_id):
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
            product_info = self._does_cart_product_exist(customer_id, product_id)
            if product_info is not None:
                if product_info[0]['Quantity'] > quantity:
                    # If the quantity is greater than the quantity to remove, update the quantity
                    self.cursor.execute("UPDATE Cart SET Quantity = Quantity - ? WHERE Customer_ID = ? AND Product_ID = ?", (quantity, customer_id, product_id))
                else:
                    self.cursor.execute("DELETE FROM Cart WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id))
                self.connection.commit()
                return True
        return False

    def get_all_products_in_cart(self, customer_id: int):
        """
        Returns the product ids of all products in the cart. 
        search_product_by_id() can then be used to get the details.
        """
        self.cursor.execute("SELECT Product.*, ProductThumbnail.ImageName, Cart.Quantity FROM Cart INNER JOIN Product ON Cart.Product_ID = Product.Product_ID INNER JOIN ProductThumbnail ON Product.Product_ID = ProductThumbnail.Product_ID WHERE Customer_ID = ?", (customer_id,))
        rows = self.cursor.fetchall()
        return rows

    def get_Specific_Customer_Review(self, customer_id: int, product_id: int):
        """Gets specific customer review from db"""
        self.cursor.execute("SELECT ProductReviews.Product_ID AS Product_ID," +
                                " ProductReviews.Customer_ID AS Customer_ID," +
                                " ProductReviews.Rating AS Rating," +
                                " ProductReviews.Review AS Review," +
                                " ProductReviews.DateOfReview AS DateOfReview" +
                                ", CustomerUser.Username FROM ProductReviews INNER JOIN CustomerUser ON ProductReviews.Customer_ID = CustomerUser.Customer_ID WHERE ProductReviews.Customer_ID = ? AND ProductReviews.Product_ID = ?", (customer_id, product_id))
        return self.cursor.fetchone()

    def get_product_review_average(self, product_id: int):
        """Gets all reviews of a product from db"""
        self.cursor.execute("SELECT AVG(Rating) AS AverageRating FROM ProductReviews WHERE Product_ID = ? ORDER BY DateOfReview DESC", (product_id,))
        data = self.cursor.fetchone()
        return data['AverageRating']
    
    def get_all_reviews_of_product_except_customer(self, customer_id: int, product_id: int):
        """Gets all reviews of a product from db except the customer's review"""
        if self._does_customer_id_exist(customer_id) is False:
            self.cursor.execute("SELECT ProductReviews.Product_ID AS Product_ID," +
                                " ProductReviews.Customer_ID AS Customer_ID," +
                                " ProductReviews.Rating AS Rating," +
                                " ProductReviews.Review AS Review," +
                                " ProductReviews.DateOfReview AS DateOfReview" +
                                ", CustomerUser.Username AS Username FROM ProductReviews INNER JOIN CustomerUser ON ProductReviews.Customer_ID = CustomerUser.Customer_ID WHERE ProductReviews.Product_ID = ? ORDER BY ProductReviews.DateOfReview ASC", (product_id,))
        else:
            self.cursor.execute("SELECT ProductReviews.Product_ID AS Product_ID," +
                                " ProductReviews.Customer_ID AS Customer_ID," +
                                " ProductReviews.Rating AS Rating," +
                                " ProductReviews.Review AS Review," +
                                " ProductReviews.DateOfReview AS DateOfReview" +
                                ", CustomerUser.Username FROM ProductReviews INNER JOIN CustomerUser ON ProductReviews.Customer_ID = CustomerUser.Customer_ID WHERE ProductReviews.Product_ID = ? AND ProductReviews.Customer_ID != ? ORDER BY ProductReviews.DateOfReview ASC", (product_id, customer_id,))
        data = self.cursor.fetchall()
        if len(data) == 0:
            return None
        return data
        
    def add_review_to_product(self, customer_id: int, product_id: int, rating:int, review: str) -> bool:
        """Inserts a review for a product into the db"""
        customer_exists = self._does_customer_id_exist(customer_id)
        product_exists = self._does_product_exist(product_id)
        review_exists = self._does_Review_Of_Product_exist(customer_id, product_id)
        if customer_exists and product_exists and not review_exists:
            self.cursor.execute("INSERT INTO ProductReviews (Customer_ID, Product_ID, Rating, Review, DateOfReview) VALUES (?, ?, ?, ?, strftime('%Y-%m-%d', 'now'))", (customer_id, product_id, rating, review))
            self.connection.commit()
            return True
        return False

    def add_payment_type(self, payment_type_name: str):
        """Adds a new payment type to the db"""
        self.cursor.execute("INSERT INTO PaymentType (PaymentTypeName) VALUES (?)", (payment_type_name,))
        self.connection.commit()
        return True

    def add_new_credit_card(self, customer_id: int, payment_info: dict):
        """Adds a new credit card to the db"""
        self.cursor.execute(
            """
            INSERT INTO CreditCard 
            (
                Customer_ID, 
                Card_ID, 
                Address1, 
                Address2, 
                Country, 
                State, 
                City, 
                ZipCode, 
                NameOnCard,
                CardNumber, 
                ExpDate, 
                CVC
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            (
                customer_id, 
                self._new_card_id(), 
                payment_info["address1"], 
                payment_info["address2"], 
                payment_info["country"], 
                payment_info["state"], 
                payment_info["city"], 
                payment_info["zip"], 
                payment_info["name_on_card"],
                payment_info["card_number"], 
                payment_info["expiration_date"], 
                payment_info["cvc"]
            )
        )
        self.connection.commit()
        return True
    
    def get_credit_card_details(self, customer_id: int):
        """Gets the details of a credit card from the db"""
        self.cursor.execute("SELECT * FROM CreditCard WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchone()

    def add_new_paypal(self, customer_id: int, email: str):
        """Adds a new paypal account to the db"""
        self.cursor.execute(
            "INSERT INTO Paypal (Customer_ID, Paypal_ID, Email) VALUES (?, ?, ?)", 
            (customer_id, self._new_paypal_id(), email)
        )
        self.connection.commit()
        return True

    def get_paypal_details(self, customer_id: int):
        """Gets the details of a paypal account from the db"""
        self.cursor.execute("SELECT * FROM Paypal WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchone()
    
    def _does_payment_method_exist(self, customer_id: int, payment_method_id: int, payment_type_name: str):
        """
        This function checks if there is a credit card or paypal 
        account for a particular user already in the db
        """
        # Check for any credit card payment methods
        if payment_type_name == "credit_card":
            self.cursor.execute(
                "SELECT * FROM CreditCard WHERE Customer_ID = ? AND Card_ID = ?", 
                (customer_id, payment_method_id)
            )
            if len(self.cursor.fetchall()) == 0:
                return False
        # Check for any paypal payment methods
        elif payment_type_name == "paypal":
            self.cursor.execute(
                "SELECT * FROM Paypal WHERE Customer_ID = ? AND Paypal_ID = ?", 
                (customer_id, payment_method_id)
            )
            if len(self.cursor.fetchall()) == 0:
                return False
        else:
            return False

        return True

    def get_individual_purchase_details(self, customer_id: int, payment_method_id: int, payment_type_name: str):
        """
        Gets any details of a recorded purchase from the db. This includes the Customer_ID, 
        PaymentMethod_ID, PaymentTypeName, and Amount.

        NOTE: (Customer_ID, PaymentMethod_ID) is the primary keys for the appropriate payment 
        method tables Paypal or CreditCard. The value PaymentTypeName is used to determine 
        which payment method table to query if that information is needed.
        """
        self.cursor.execute(
            "SELECT * FROM Purchase WHERE Customer_ID = ? AND PaymentMethod_ID = ? AND PaymentTypeName = ?", 
            (customer_id, payment_method_id, payment_type_name)
        )
        return self.cursor.fetchone()

    def get_all_purchase_details(self, customer_id: int):
        """ Gets all purchase details from the db for a given customer. """
        self.cursor.execute("SELECT * FROM Purchase WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchall()

    def add_new_order(self, customer_id: int, payment_info: dict, address_info: dict, products_to_order: List[Tuple[int, int]]):
        """
        Performs a transaction that updates Purchase, Orders, and ProductsInOrder tables.
        A valid payment method is required to exist in the db for the customer prior to 
        calling.

        NOTE: in reality, a payment gateway would be used here, but since this is for a db 
        class and is not real, we'll just assume the payment is valid if its in the db.
        """
        # validate there is a valid payment method for this customer
        valid_payment_method = self._does_payment_method_exist(
            customer_id, payment_info["payment_method_id"], payment_info["payment_type_name"]
        )

        # validate all items are in stock
        all_products_in_stock = True
        for (product_id, quantity) in products_to_order:
            if not self._does_product_exist(product_id):
                all_products_in_stock = False
                break
            if self.product_stock(product_id) < quantity:
                all_products_in_stock = False
                break

        if valid_payment_method and all_products_in_stock:
            order_id = self._new_order_id()

            self.cursor.execute("BEGIN TRANSACTION")
            self.cursor.execute(  # insert purchase info into Purchase table
                """
                INSERT INTO Purchase 
                (
                    Customer_ID, 
                    PaymentMethod_ID, 
                    PaymentTypeName, 
                    Amount
                ) VALUES (?, ?, ?, ?)
                """, 
                (
                    customer_id, 
                    payment_info["payment_method_id"], 
                    payment_info["payment_type_name"], 
                    payment_info["purchase_amount"]
                )
            )
            self.cursor.execute(  # insert order details into Orders table
                """
                INSERT INTO Orders 
                (
                    Order_ID,
                    Customer_ID, 
                    PaymentMethod_ID, 
                    PaymentTypeName, 
                    DateOfPurchase,
                    StatusName, 
                    FirstName, 
                    LastName, 
                    Address1, 
                    Address2, 
                    Country, 
                    State, 
                    City, 
                    ZipCode, 
                    PhoneNumber
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, 
                (
                    order_id,
                    customer_id,
                    payment_info["payment_method_id"],
                    payment_info["payment_type_name"],
                    address_info["date_of_purchase"],
                    self.default_order_status,
                    address_info["first_name"],
                    address_info["last_name"],
                    address_info["address1"],
                    address_info["address2"],
                    address_info["country"],
                    address_info["state"],
                    address_info["city"],
                    address_info["zip"],
                    address_info["phone"]
                )
            )
            # insert details of each product in order into ProductsInOrder table
            for (product_id, quantity) in products_to_order:
                self.cursor.execute(
                    """
                    INSERT INTO ProductsInOrder
                    (
                        Order_ID,
                        Product_ID,
                        Quantity,
                        PriceSold,
                        DateSold
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        product_id,
                        quantity,
                        self.product_price(product_id),
                        address_info["date_of_purchase"]
                    )
                )
            self.connection.commit()
            return True
        return False

    def get_order_details(self, order_id: int):
        """Gets the details of an order from the db"""

        # get all order details
        self.cursor.execute("SELECT * FROM Orders WHERE Order_ID = ?", (order_id,))
        order_details = self.cursor.fetchone()

        if not (order_details == None): 

            # get payment details
            customer_id = order_details[1]
            payment_method_id = order_details[2]
            payment_type_name = order_details[3]
            payment_details = self.get_individual_purchase_details(
                customer_id, payment_method_id, payment_type_name
            )

            # get all products from the order
            self.cursor.execute(
                "SELECT * FROM ProductsInOrder WHERE Order_ID = ?", 
                (order_id,)
            )
            products_in_order = self.cursor.fetchall()

            return order_details, payment_details, products_in_order

        return None

    def get_order_history(self, customer_id: int):
        """
        Gets all order ids associated with this customer. 
        get_order_details() can be used for the details
        """
        self.cursor.execute("SELECT Order_ID FROM Orders WHERE Customer_ID = ?", (customer_id,))
        return self.cursor.fetchall()

    def get_all_orders(self, op_status_filter: str = None, op_orderId_filter: int = None):
        """Gets all orders from the db. If op_status_filter is provided, only orders with that status are returned.
        If op_orderId_filter is provided, only orders with that order id are returned. if both are provided, 
        only orders with that status and order id are returned."""
        
        if op_status_filter is not None and op_orderId_filter is not None:
            self.cursor.execute("SELECT * FROM Orders WHERE StatusName = ? AND Order_ID = ?", (op_status_filter, op_orderId_filter))
        elif op_status_filter is not None:
            self.cursor.execute("SELECT * FROM Orders WHERE StatusName = ?", (op_status_filter,))
        elif op_orderId_filter is not None:
            self.cursor.execute("SELECT * FROM Orders WHERE Order_ID = ?", (op_orderId_filter,))
        else:
            self.cursor.execute("SELECT * FROM Orders")
        return self.cursor.fetchall()

    def cancel_order(self, order_id: int):
        self.cursor.execute("UPDATE Orders SET StatusName = ? WHERE Order_ID = ?", ("Cancelled", order_id))
        self.connection.commit()
        return True

    def update_order_status_to_shipped(self, order_id: int):
        self.cursor.execute("UPDATE Orders SET StatusName = ? WHERE Order_ID = ?", ("Shipped", order_id))
        self.connection.commit()
        return True

    def update_order_status_to_delivered(self, order_id: int):
        self.cursor.execute("UPDATE Orders SET StatusName = ? WHERE Order_ID = ?", ("Delivered", order_id))
        self.connection.commit()
        return True

    def get_order_status(self, order_id: int):
        self.cursor.execute("SELECT StatusName FROM Orders WHERE Order_ID = ?", (order_id,))
        return self.cursor.fetchone()[0]
    
    def get_all_order_statuses(self):
        """Gets all order statuses from the db"""
        self.cursor.execute("SELECT * FROM OrderStatus")
        return self.cursor.fetchall()

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

    def _does_cart_product_exist(self, customer_id: int, product_id: int):
        """Checks if product is in the cart for the customer"""
        self.cursor.execute("SELECT Customer_ID, Product_ID Quantity FROM Cart WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id,))
        data = self.cursor.fetchall()
        if len(data) != 0:
            return data
        return None
    
    def _does_Wishlist_Product_exist(self, customer_id: int, product_id: int):
        """Checks if product is in the cart for the customer"""
        self.cursor.execute("SELECT Customer_ID, Product_ID FROM Wishlist WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id,))
        data = self.cursor.fetchall()
        if len(data) != 0:
            return data
        return None

    def _does_Review_Of_Product_exist(self, customer_id: int, product_id: int) -> bool:
        """Checks if product is in the cart for the customer"""
        self.cursor.execute("SELECT Customer_ID, Product_ID FROM ProductReviews WHERE Customer_ID = ? AND Product_ID = ?", (customer_id, product_id,))
        data = self.cursor.fetchall()
        if len(data) != 0:
            return True
        return False
    
    def _does_Product_Exist_In_Customer_Orders(self, customer_id: int, product_id: int) -> bool:
        """Checks if product has been ordered by the customer"""
        self.cursor.execute("SELECT Orders.Order_ID, Orders.Customer_ID, ProductsInOrder.Product_ID FROM Orders INNER JOIN ProductsInOrder ON Orders.Order_ID = ProductsInOrder.Order_ID WHERE Orders.Customer_ID = ? AND ProductsInOrder.Product_ID = ?", (customer_id, product_id,))
        data = self.cursor.fetchall()
        if len(data) != 0:
            return True
        return False
        

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

    def _new_paypal_id(self) -> int:
        """generate new paypal id artifical key"""
        self.cursor.execute("SELECT MAX(Paypal_ID) FROM Paypal")
        max_paypal_id = self.cursor.fetchone()[0]
        if max_paypal_id is None:
            return 0
        return max_paypal_id + 1

    def _new_card_id(self) -> int:
        """generate new card id artifical key"""
        self.cursor.execute("SELECT MAX(Card_ID) FROM CreditCard")
        max_card_id = self.cursor.fetchone()[0]
        if max_card_id is None:
            return 0
        return max_card_id + 1

    def _new_payment_id(self) -> int:
        """generate new payment id artifical key"""
        self.cursor.execute("SELECT MAX(Payment_ID) FROM Payment")
        max_payment_id = self.cursor.fetchone()[0]
        if max_payment_id is None:
            return 0
        return max_payment_id + 1

    def _new_order_id(self) -> int:
        """generate new order id artifical key"""
        self.cursor.execute("SELECT MAX(Order_ID) FROM Orders")
        max_order_id = self.cursor.fetchone()[0]
        if max_order_id is None:
            return 0
        return max_order_id + 1