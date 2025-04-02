create table AdminUser(
	Admin_ID INT,
	Username Varchar(16) 
        CONSTRAINT AdminUser_Username_NOTNULL NOT NULL
    ,
	Password Varchar(64) 
        CONSTRAINT AdminUser_Password_NOTNULL NOT NULL
    ,
	Email Varchar(254) 
        CONSTRAINT AdminUser_Email_NOTNULL NOT NULL
        CONSTRAINT AdminUser_Email_Format CHECK (Email LIKE '_%@_%._%')
    ,
	CONSTRAINT AdminUser_PK PRIMARY KEY (Admin_ID)
);

create table CustomerUser(
	Customer_ID INT,
	Username Varchar(16) 
        CONSTRAINT CustomerUser_Username_NOTNULL NOT NULL
    ,
	Email Varchar(254) 
        CONSTRAINT CustomerUser_Email_NOTNULL NOT NULL
        CONSTRAINT CustomerUser_Email_Format CHECK (Email LIKE '_%@_%._%')
    ,
	Password Varchar(64) 
        CONSTRAINT CustomerUser_Password_NOTNULL NOT NULL
    ,
	Phone_Number INT 
        CONSTRAINT CustomerUser_Phone_Number_NOTNULL NOT NULL
        CONSTRAINT CustomerUser_PhoneNumber_Format CHECK (Phone_Number BETWEEN 0000000000 AND 9999999999)
    ,
	CONSTRAINT CustomerUser_PK PRIMARY KEY(Customer_ID)
);

create table Cart(
	Customer_ID INT,
	Product_ID INT,
	CONSTRAINT Cart_PK PRIMARY KEY(Customer_ID, Product_ID),
	CONSTRAINT Cart_Customer_ID_FK FOREIGN KEY(Customer_ID) REFERENCES CustomerUser(Customer_ID) ON DELETE CASCADE, 
	CONSTRAINT Cart_Product_ID_FK FOREIGN KEY(Product_ID) REFERENCES Product(Product_ID) ON DELETE CASCADE
);

create table Wishlist(
	Customer_ID INT,
	Product_ID INT,
	CONSTRAINT Wishlist_PK PRIMARY KEY(Customer_ID, Product_ID),
	CONSTRAINT Wishlist_Customer_ID_FK FOREIGN KEY(Customer_ID) REFERENCES CustomerUser(Customer_ID) ON DELETE CASCADE,
	CONSTRAINT Wishlist_Product_ID_FK FOREIGN KEY(Product_ID) REFERENCES Product(Product_ID) ON DELETE CASCADE
);

create table Product(
	Product_ID INT,
	Title Varchar(255) 
        CONSTRAINT Product_Title_NOTNULL NOT NULL
    ,
	Price Numeric(8,2) 
        CONSTRAINT Product_Price_NOTNULL NOT NULL
        CONSTRAINT Product_Price_NonNegative CHECK (Price >= 0)
    ,
	Stock INT 
        CONSTRAINT Product_Stock_NOTNULL NOT NULL
        CONSTRAINT Product_Stock_NonNegative CHECK (Stock >= 0)
    ,
	Description Varchar(1000),
	DiscountPercentage INT
        CONSTRAINT Product_DiscountPercentage_Format CHECK (DiscountPercentage between 0 and 99)
    ,
	WebsiteInfo Varchar(500),
	DateCreated Date 
        CONSTRAINT Product_DateCreated_NOTNULL NOT NULL
    ,
	CONSTRAINT Product_PK PRIMARY KEY(Product_ID)
);

create table ProductImages(
	Product_ID INT,
	ImageName Varchar(255)
		CONSTRAINT ProductImages_Name_NOTNULL NOT NULL
	,
	ImageData BLOB
        CONSTRAINT ProductImages_Image_NOTNULL NOT NULL
    ,
	CONSTRAINT ProductImages_PK PRIMARY KEY(Product_ID, ImageName)
);

create table ProductThumbnail(
	Product_ID INT,
	ImageName Varchar(255)
		CONSTRAINT ProductImages_Name_NOTNULL NOT NULL
	,
	ImageData BLOB
        CONSTRAINT ProductImages_Image_NOTNULL NOT NULL
    ,
	CONSTRAINT ProductImages_PK PRIMARY KEY(Product_ID)
);


create table ProductCategories(
	CategoryName Varchar(100),
	CONSTRAINT ProductCategories_PK PRIMARY KEY(CategoryName)
);

create table ProductCategory(
	Product_ID INT,
	CategoryName Varchar,
	CONSTRAINT ProductCategory_PK PRIMARY KEY(Product_ID, CategoryName),
	CONSTRAINT ProductCategory_Product_ID_FK FOREIGN KEY(CategoryName) REFERENCES ProductCategories(CategoryName) ON DELETE CASCADE
);

create table Orders(
	Order_ID INT,
	Payment_ID INT,
	Customer_ID INT,
	DateOfPurchase DATE
        CONSTRAINT Order_DateOfPurchase_NOTNULL NOT NULL
    ,
	StatusName Varchar(100),
	FirstName Varchar(25)
        CONSTRAINT Order_FirstName_NOTNULL NOT NULL
    ,
	LastName Varchar(25)
        CONSTRAINT Order_LastName_NOTNULL NOT NULL
    ,
	Address1 Varchar(300)
        CONSTRAINT Order_Address1_NOTNULL NOT NULL
    ,
	Address2 Varchar(300),
	Country Varchar(100)
        CONSTRAINT Order_Country_NOTNULL NOT NULL
    ,
	State Varchar(100)
        CONSTRAINT Order_State_NOTNULL NOT NULL
    ,
	City Varchar(100)
        CONSTRAINT Order_City_NOTNULL NOT NULL
    ,
	ZipCode INT
        CONSTRAINT Order_ZipCode_NOTNULL NOT NULL
        CONSTRAINT Order_ZipCode_Format CHECK (ZipCode BETWEEN 00000 AND 99999)
    ,
	PhoneNumber INT
        CONSTRAINT Order_PhoneNumber_NOTNULL NOT NULL
        CONSTRAINT Order_PhoneNumber_Format CHECK (PhoneNumber BETWEEN 0000000000 AND 9999999999)
    ,
	CONSTRAINT Order_PK PRIMARY KEY(Order_ID),
	CONSTRAINT Order_Payment_ID_FK FOREIGN KEY(Payment_ID) REFERENCES Payment(Payment_ID) ON DELETE SET NULL,
	CONSTRAINT Order_Customer_ID_FK FOREIGN KEY(Customer_ID) REFERENCES CustomerUser(Customer_ID) ON DELETE SET NULL,
	CONSTRAINT Order_StatusName_FK FOREIGN KEY(StatusName) REFERENCES OrderStatus(Name) ON DELETE SET NULL
);

create table ProductsInOrder(
	Order_ID INT,
	Product_ID INT,
	Quantity INT
		CONSTRAINT ProductsInOrder_Quantity_NOTNULL NOT NULL
		CONSTRAINT ProductsInOrder_Quantity_NonNegative CHECK (Quantity >= 0)
	,
	PriceSold Numeric(8,2)
        CONSTRAINT ProductsInOrder_PriceSold_NOTNULL NOT NULL
    	CONSTRAINT ProductsInOrder_PriceSold_NonNegative CHECK (PriceSold >= 0)
    ,
	DateSold Date 
		CONSTRAINT ProductsInOrder_DateSold_NOTNULL NOT NULL
	,
	CONSTRAINT ProductsInOrder_PK PRIMARY KEY(Order_ID, Product_ID),
	CONSTRAINT ProductsInOrder_Order_ID_FK FOREIGN KEY(Order_ID) REFERENCES Orders(Order_ID) ON DELETE CASCADE,
	CONSTRAINT ProductsInOrder_Product_ID_FK FOREIGN KEY(Product_ID) REFERENCES Product(Product_ID) ON DELETE CASCADE
);

create table OrderStatus(
	Name Varchar(100),
	Description VarChar(1000),
	CONSTRAINT OrderStatus_PK PRIMARY KEY(Name)
);

create table PaymentType(
	PaymentName Varchar(100),
	CONSTRAINT PaymentType_PK PRIMARY KEY(PaymentName)
);

/*
Payment_ID in all payment types schemas need to be unique 
*/
create table Payment(
	Payment_ID INT,
	PaymentName Varchar(100),
	Amount Numeric(8,2)
        CONSTRAINT Payment_Amount_NOTNULL NOT NULL
        CONSTRAINT Payment_Amount_NonNegative CHECK (Amount >= 0)
    ,
	CONSTRAINT Payment_PK PRIMARY KEY(Payment_ID),
	CONSTRAINT Payment_PaymentName_FK FOREIGN KEY(PaymentName) REFERENCES PaymentType(PaymentName) ON DELETE SET NULL
);

create table Paypal(
	Payment_ID INT,
	Email Varchar(254)
        CONSTRAINT Paypal_Email_NOTNULL NOT NULL
        CONSTRAINT Paypal_Email_Format CHECK (Email LIKE '%@%.%')
    ,
	CONSTRAINT Paypal_PK PRIMARY KEY(Payment_ID),
	CONSTRAINT Paypal_Payment_ID_FK FOREIGN KEY(Payment_ID) REFERENCES Payment(Payment_ID)
);

create table CreditCard(
	Payment_ID INT,
	Address1 Varchar(300)
        CONSTRAINT CreditCard_Address1_NOTNULL NOT NULL
    ,
	Address2 Varchar(300),
	Country Varchar(100)
        CONSTRAINT CreditCard_Country_NOTNULL NOT NULL
    ,
	State Varchar(100)
        CONSTRAINT CreditCard_State_NOTNULL NOT NULL
    ,
	City Varchar(100)
        CONSTRAINT CreditCard_City_NOTNULL NOT NULL
    ,
	ZipCode INT
        CONSTRAINT CreditCard_ZipCode_NOTNULL NOT NULL
        CONSTRAINT CreditCard_ZipCode_Format CHECK (ZipCode BETWEEN 00000 AND 99999)
    ,
	NameOnCard Varchar(100)
        CONSTRAINT CreditCard_NameOnCard_NOTNULL NOT NULL
    ,
	CardNumber INT
        CONSTRAINT CreditCard_CardNumber_NOTNULL NOT NULL
        CONSTRAINT CreditCard_CardNumber_Format CHECK (CardNumber BETWEEN 0000000000000000 AND 9999999999999999)
    ,
	CVC INT
        CONSTRAINT CreditCard_CVC_NOTNULL NOT NULL
        CONSTRAINT CreditCard_CVC_Format CHECK (CVC BETWEEN 000 AND 999)
    ,
	ExpDate DATE
        CONSTRAINT CreditCard_ExpDate_NOTNULL NOT NULL
    ,
	CONSTRAINT CreditCard_PK PRIMARY KEY(Payment_ID),
    CONSTRAINT CreditCard_Payment_ID_FK FOREIGN KEY(Payment_ID) REFERENCES Payment(Payment_ID)
);

create table ProductReviews(
	Product_ID INT,
	Customer_ID INT,
	Rating INT
		CONSTRAINT ProductReviews_Rating_NOTNULL NOT NULL
		CONSTRAINT ProductReviews_Rating_Format CHECK (Rating BETWEEN 1 AND 5)
	,
	Review Varchar(1000)
		CONSTRAINT ProductReviews_Review_NOTNULL NOT NULL
	,
	DateOfReview Date 
		CONSTRAINT ProductReviews_DateOfReview_NOTNULL NOT NULL
	,
	CONSTRAINT ProductReviews_PK PRIMARY KEY(Product_ID, Customer_ID),
	CONSTRAINT ProductReviews_Product_ID_FK FOREIGN KEY(Product_ID) REFERENCES Product(Product_ID) ON DELETE CASCADE,
	CONSTRAINT ProductReviews_Customer_ID_FK FOREIGN KEY(Customer_ID) REFERENCES CustomerUser(Customer_ID) ON DELETE CASCADE
);