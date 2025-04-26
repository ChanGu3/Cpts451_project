/*
used some random data for testing generated using chatgpt and then revised for proper use
    - Some Values may need to be changed like the passwords since they will be hashed in later versions
*/

/* Do this using script in data folder */ 
/* INSERT INTO AdminUser VALUES(2, 'admin2', 'password123', 'admin2@example.com');*/ 
INSERT INTO AdminUser (Admin_ID, Username, Password, Email) VALUES
(1, 'admin1', 'password1', 'admin1@example.com'),
(2, 'admin2', 'password2', 'admin2@example.com'),
(3, 'admin3', 'password3', 'admin3@example.com');

-- Customer Users
INSERT INTO CustomerUser (Customer_ID, Username, Email, Password, Phone_Number) VALUES
(1, 'john_doe', 'john.doe@example.com', 'password123', '1234567890'),
(2, 'jane_smith', 'jane.smith@example.com', 'password456', '2345678901'),
(3, 'alice_jones', 'alice.jones@example.com', 'password789', '3456789012'),
(4, 'bob_brown', 'bob.brown@example.com', 'password101', '4567890123'),
(5, 'carol_white', 'carol.white@example.com', 'password202', '5678901234'),
(6, 'dave_black', 'dave.black@example.com', 'password303', '6789012345'),
(7, 'eve_green', 'eve.green@example.com', 'password404', '7890123456'),
(8, 'frank_blue', 'frank.blue@example.com', 'password505', '8901234567'),
(9, 'grace_red', 'grace.red@example.com', 'password606', '9012345678'),
(10, 'hank_yellow', 'hank.yellow@example.com', 'password707', '0123456789');

-- Products
INSERT INTO Product (Product_ID, Title, Price, Stock, Description, DiscountPercentage, WebsiteInfo, DateCreated) VALUES
(1, 'Laptop', 999.99, 50, 'High-performance laptop', 10, 'www.example.com/laptop', '2025-04-01'),
(2, 'Smartphone', 499.99, 100, 'Latest model smartphone', 15, 'www.example.com/smartphone', '2025-04-02'),
(3, 'Headphones', 199.99, 200, 'Noise-cancelling headphones', 5, 'www.example.com/headphones', '2025-04-03'),
(4, 'Smartwatch', 299.99, 150, 'Fitness tracking smartwatch', 20, 'www.example.com/smartwatch', '2025-04-04'),
(5, 'Tablet', 399.99, 80, 'Portable tablet for work and play', 8, 'www.example.com/tablet', '2025-04-05'),
(6, 'Camera', 799.99, 30, 'Digital camera with high resolution', 12, 'www.example.com/camera', '2025-04-06'),
(7, 'Printer', 149.99, 60, 'Wireless color printer', 10, 'www.example.com/printer', '2025-04-07'),
(8, 'Monitor', 249.99, 120, '27-inch 4K monitor', 18, 'www.example.com/monitor', '2025-04-08'),
(9, 'Keyboard', 49.99, 200, 'Mechanical keyboard with RGB lighting', 5, 'www.example.com/keyboard', '2025-04-09'),
(10, 'Mouse', 29.99, 300, 'Ergonomic wireless mouse', 10, 'www.example.com/mouse', '2025-04-10'),
(11, 'Mouse 2', 29.99, 300, 'Ergonomic wireless mouse', 10, 'www.example.com/mouse', '2025-04-10');

-- Carts
INSERT INTO Cart (Customer_ID, Product_ID, Quantity) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 1),
(4, 4, 3),
(5, 5, 2),
(6, 6, 1),
(7, 7, 4),
(8, 8, 1),
(9, 9, 5),
(10, 10, 2);

-- Wishlists
INSERT INTO Wishlist (Customer_ID, Product_ID) VALUES
(1, 2),
(2, 3),
(3, 4),
(4, 5),
(5, 6),
(6, 7),
(7, 8),
(8, 9),
(9, 10),
(10, 1);

-- Order Statuses
INSERT INTO OrderStatus (Name, Description) VALUES
('Pending', 'Order has been placed but not yet processed'),
('Shipped', 'Order has been shipped'),
('Delivered', 'Order has been delivered to the customer'),
('Cancelled', 'Order has been cancelled by the customer');

-- Payment Types
INSERT INTO PaymentType (PaymentTypeName) VALUES
('Credit Card'),
('PayPal'),
('Bank Transfer'),
('Cash on Delivery');

-- Orders
INSERT INTO Orders (Order_ID, Customer_ID, PaymentMethod_ID, PaymentTypeName, DateOfPurchase, StatusName, FirstName, LastName, Address1, Address2, Country, State, City, ZipCode, PhoneNumber) VALUES
(6, 6, 2, 'PayPal', '2025-04-16', 'Shipped', 'Dave', 'Black', '303 Cedar St', 'Suite 9F', 'USA', 'WA', 'Pullman', '99168', '6789012345'),
(7, 7, 1, 'Credit Card', '2025-04-17', 'Delivered', 'Eve', 'Green', '404 Walnut St', '', 'USA', 'WA', 'Pullman', '99169', '7890123456'),
(8, 8, 2, 'PayPal', '2025-04-18', 'Pending', 'Frank', 'Blue', '505 Aspen St', '', 'USA', 'WA', 'Pullman', '99170', '8901234567'),
(9, 9, 1, 'Credit Card', '2025-04-19', 'Shipped', 'Grace', 'Red', '606 Cherry St', 'Unit A', 'USA', 'WA', 'Pullman', '99171', '9012345678'),
(10, 10, 2, 'PayPal', '2025-04-20', 'Delivered', 'Hank', 'Yellow', '707 Spruce St', 'Floor 2B', 'USA', 'WA', 'Pullman', '99172', '0123456789'),
(11, 1, 1, 'Credit Card', '2025-04-21', 'Cancelled', 'John', 'Doe', '123 Main St', 'Apt 4B', 'USA', 'WA', 'Pullman', '99163', '1234567890'),
(12, 2, 2, 'PayPal', '2025-04-22', 'Pending', 'Jane', 'Smith', '456 Oak St', 'Suite 5A', 'USA', 'WA', 'Pullman', '99164', '2345678901'),
(13, 3, 1, 'Credit Card', '2025-04-23', 'Delivered', 'Alice', 'Jones', '789 Pine St', 'Unit 6C', 'USA', 'WA', 'Pullman', '99165', '3456789012'),
(14, 4, 2, 'PayPal', '2025-04-24', 'Shipped', 'Bob', 'Brown', '101 Maple St', 'Floor 7D', 'USA', 'WA', 'Pullman', '99166', '4567890123'),
(15, 5, 1, 'Credit Card', '2025-04-25', 'Delivered', 'Carol', 'White', '202 Birch St', 'Apt 8E', 'USA', 'WA', 'Pullman', '99167', '5678901234');

INSERT INTO ProductsInOrder (Order_ID, Product_ID, Quantity, PriceSold, DateSold) VALUES
(1, 1, 1, 999.99, '2025-04-11'),
(2, 2, 2, 499.99, '2025-04-12'),
(3, 3, 1, 199.99, '2025-04-13'),
(4, 4, 1, 299.99, '2025-04-14'),
(5, 5, 2, 399.99, '2025-04-15'),
(6, 6, 1, 799.99, '2025-04-16'),
(7, 7, 2, 149.99, '2025-04-17'),
(8, 8, 1, 249.99, '2025-04-18'),
(9, 9, 3, 49.99, '2025-04-19'),
(10, 10, 2, 29.99, '2025-04-20'),
(11, 2, 1, 499.99, '2025-04-21'),
(12, 3, 1, 199.99, '2025-04-22'),
(13, 4, 1, 299.99, '2025-04-23'),
(14, 5, 1, 399.99, '2025-04-24'),
(15, 6, 1, 799.99, '2025-04-25');