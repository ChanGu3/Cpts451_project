/*
used some random data for testing generated using chatgpt and then revised for proper use
    - Some Values may need to be changed like the passwords since they will be hashed in later versions
*/

INSERT INTO AdminUser VALUES(1, 'admin1', 'password123');

INSERT INTO CustomerUser VALUES
(1, 'customer1@example.com', 'password1', 1234567890),
(2, 'customer2@example.com', 'password2', 2345678901),
(3, 'customer3@example.com', 'password3', 3456789012),
(4, 'customer4@example.com', 'password4', 4567890123);

INSERT INTO Product VALUES
(1, 'Product A', 10.99, 100, 'Description of Product A', 10, 'www.productA.com', '2025-FEB-25'),
(2, 'Product B', 20.99, 50, 'Description of Product B', 15, 'www.productB.com', '2025-FEB-20'),
(3, 'Product C', 30.99, 200, 'Description of Product C', 5, 'www.productC.com', '2025-FEB-18'),
(4, 'Product D', 40.99, 300, 'Description of Product D', 20, 'www.productD.com', '2025-FEB-15');

INSERT INTO Cart VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 4);

INSERT INTO Wishlist VALUES
(1, 3),
(2, 1),
(3, 2),
(4, 4);

INSERT INTO ProductImages VALUES
(1, 'image1_blob_data'),
(2, 'image2_blob_data'),
(3, 'image3_blob_data'),
(4, 'image4_blob_data');

INSERT INTO ProductCategories VALUES
('Electronics'),
('Furniture'),
('Clothing'),
('Books');

INSERT INTO ProductCategory VALUES
(1, 'Electronics'),
(2, 'Furniture'),
(3, 'Clothing'),
(4, 'Books');

INSERT INTO OrderStatus VALUES
('Pending', 'Order is pending payment'),
('Shipped', 'Order has been shipped'),
('Delivered', 'Order has been delivered'),
('Cancelled', 'Order has been cancelled');

INSERT INTO PaymentType VALUES
('CreditCard'),
('Paypal');

/*
Product_ID needs to be inforced to be unique in each payment type through this payment
*/
INSERT INTO Payment VALUES
(1, 'CreditCard', 100.00),
(2, 'Paypal', 50.00),
(3, 'CreditCard', 150.00);

INSERT INTO Paypal VALUES
(2, 'paypal2@example.com');

INSERT INTO CreditCard VALUES
(1, '123 Main St', 'Apt 4B', 'USA', 'NY', 'New York', 10001, 'John Doe', 1234567890123456, 123, '2025-DEC-31'),
(3, '789 Pine St', 'Suite 2', 'USA', 'TX', 'Dallas', 75201, 'Mark Johnson', 3456789012345678, 789, '2025-OCT-15');

INSERT INTO Orders VALUES
(1, 1, 1, '2025-FEB-25', 'Pending', 'John', 'Doe', '123 Main St', '', 'USA', 'NY', 'New York', 10001, 1234567890),
(2, 2, 2, '2025-FEB-24', 'Shipped', 'Jane', 'Smith', '456 Oak St', '', 'USA', 'CA', 'Los Angeles', 90001, 2345678901),
(3, 3, 3, '2025-FEB-23', 'Delivered', 'Mark', 'Johnson', '789 Pine St', 'Suite 2', 'USA', 'TX', 'Dallas', 75201, 3456789012);

INSERT INTO ProductsInOrder VALUES
(1, 1, 10.99),
(1, 2, 20.99),
(2, 3, 30.99),
(3, 4, 40.99);
