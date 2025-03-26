import pytest
from dbms import Database

"""
Note pytest will run these tests sequentially. As a result, the database will be 
modified at each test. Run ./test_backend.sh to run tests on a newly inititalizeddb.
"""

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
    success = db.admin_account_creation("test", "test", "test@test.com")
    assert success == True
    assert db._does_admin_exist("test") == True

def test_valid_customer_credentials_verification():
    db = Database("database.db")
    assert db._does_customer_exist("test") 
    assert db.validate_customer_username_password("test", "test")
    assert db.validate_customer_id_password(0, "test")

def test_invalid_customer_password_verification():
    db = Database("database.db")
    assert db._does_customer_exist("test")
    assert not db.validate_customer_username_password("test", "tesstt")
    assert not db.validate_customer_id_password(0, "tesstt")

def test_valid_admin_password_verification():
    db = Database("database.db")
    assert db._does_admin_exist("test") 
    assert db.validate_admin_username_password("test", "test")
    assert db.validate_admin_id_password(0, "test")

def test_invalid_admin_password_verification():
    db = Database("database.db")
    assert db._does_admin_exist("test")
    assert not db.validate_admin_username_password("test", "tesstt")
    assert not db.validate_admin_id_password(0, "tesstt")

def test_insert_new_product():
    db = Database("database.db")
    db.insert_new_product(
        {
            "title": "test",
            "price": 100,
            "stock": 100,
            "description": "test",
            "discount_percentage": 10,
            "website_info": "test",
            "date_created": "2025-03-04",
            "product_id": None,
        }
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

def test_invalid_admin_add_product():
    db = Database("database.db")
    assert not db.admin_add_product(
        admin_id=0,
        admin_password="bad_password",
        product_details=        {
            "title": "new_product",
            "price": 100,
            "stock": 100,
            "description": "test",
            "discount_percentage": 10,
            "website_info": "test",
            "date_created": "2025-03-04",
            "product_id": None,
        }
    )

    assert not db._does_product_exist(1)

def test_admin_add_product():
    db = Database("database.db")
    assert db.admin_add_product(
        admin_id=0,
        admin_password="test",
        product_details=        {
            "title": "new_product",
            "price": 100,
            "stock": 100,
            "description": "test",
            "discount_percentage": 10,
            "website_info": "test",
            "date_created": "2025-03-04",
            "product_id": None,
        }
    )

    # ensure product was added to db
    product_details = db.retrieve_specific_product_details(product_id=1)
    assert product_details[0] == 1
    assert product_details[1] == "new_product"
    assert product_details[2] == 100
    assert product_details[3] == 100
    assert product_details[4] == "test"
    assert product_details[5] == 10

def test_invalid_admin_remove_product():
    """ensures admin cannot remove product from db if credentials are invalid"""
    db = Database("database.db")
    assert not db.admin_remove_product(
        admin_id=0,
        admin_password="bad_password",
        product_id=1
    )    
    assert db._does_product_exist(1)

def test_admin_remove_product():
    """ensures admin can remove product from db"""
    db = Database("database.db")
    assert db.admin_remove_product(
        admin_id=0,
        admin_password="test",
        product_id=1
    )    
    assert not db._does_product_exist(1)

def test_sign_in_customer():
    """ensures valid customer credentials return the correct user id and email"""
    db = Database("database.db")
    db.customer_account_creation("new_customer1", "test", "test@test.com", "1111111111")
    assert db.sign_in("new_customer1", "test") == (1, "test@test.com")

def test_sign_in_admin():
    """ensures valid admin credentials return the correct user id and email"""
    db = Database("database.db")
    db.admin_account_creation("new_admin1", "test", "test@test.com")
    assert db.sign_in("new_admin1", "test") == (1, "test@test.com")

def test_sign_in_invalid_customer():
    """ensures invalid customer credentials return None"""
    db = Database("database.db")
    assert db.sign_in("bad_customer_1", "bad_password_1") is None

def test_sign_in_invalid_admin():
    """ensures invalid admin credentials return None"""
    db = Database("database.db")
    assert db.sign_in("bad_admin_1", "bad_password_1") is None
    