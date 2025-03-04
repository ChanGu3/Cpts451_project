import pytest
from dbms import Database

def test_first_customer_id():
    db = Database("database.db")
    assert db._new_customer_id() == 0

def test_first_admin_id():
    db = Database("database.db")
    assert db._new_admin_id() == 0

def test_no_customer_found():
    db = Database("database.db")
    assert db._does_customer_exist("test") == False

def test_no_admin_found():
    db = Database("database.db")
    assert db._does_admin_exist("test") == False

def test_customer_account_creation():
    db = Database("database.db")
    assert db._does_customer_exist("test") == False
    success = db.customer_account_creation("test", "test", "test@test.com", "1111111111")
    assert success == True
    assert db._does_customer_exist("test") == True

def test_admin_account_creation():
    db = Database("database.db")
    assert db._does_admin_exist("test") == False
    success = db.admin_account_creation("test", "test")
    assert success == True
    assert db._does_admin_exist("test") == True

def test_valid_customer_password_verification():
    db = Database("database.db")
    assert db._does_customer_exist("test") 
    assert db.validate_customer_credentials("test", "test")

def test_invalid_customer_password_verification():
    db = Database("database.db")
    assert db._does_customer_exist("test")
    assert not db.validate_customer_credentials("test", "tesstt")

def test_valid_admin_password_verification():
    db = Database("database.db")
    assert db._does_admin_exist("test") 
    assert db.validate_admin_credentials("test", "test")

def test_invalid_admin_password_verification():
    db = Database("database.db")
    assert db._does_admin_exist("test")
    assert not db.validate_admin_credentials("test", "tesstt")

def test_insert_product_details():
    db = Database("database.db")
    db.insert_all_product_details(
        title="test",
        price=100,
        stock=100,
        description="test",
        discount_percentage=10,
        website_info="test",
        date_created="2025-03-04",
        product_id=None,  # None if no product exists in db already
    )

    # retrieve product details
    product_details = db.retrieve_all_product_details()

    print(product_details)
    assert len(product_details) == 1
    assert product_details[0][0] == 0
    assert product_details[0][1] == "test"
    assert product_details[0][2] == 100
    assert product_details[0][3] == 100
    assert product_details[0][4] == "test"
    assert product_details[0][5] == 10
    assert product_details[0][6] == "test"
    assert product_details[0][7] == "2025-03-04"