import pytest
from dbms import Database
import bcrypt

"""
Note pytest will run these tests sequentially. As a result, the database will be 
modified at each test. Run ./test_backend.sh to run tests on a newly inititalizeddb.
"""

db = Database("database.db")

def test_first_customer_id():
    assert db._new_customer_id() == 0

def test_first_admin_id():
    assert db._new_admin_id() == 0

def test_no_customer_found():
    assert db._does_customer_exist("test") == False

def test_no_admin_found():
    assert db._does_admin_exist("test") == False

def test_customer_account_creation():
    assert db._does_customer_exist("test") == False
    success = db.customer_account_creation("test", "test", "test@test.com", "1111111111")
    assert success == True
    assert db._does_customer_exist("test") == True

def test_get_customer_info():
    assert len(db.get_customer_info(0)) == 5
    details = db.get_customer_info(0)
    assert details[0] == 0
    assert details[1] == "test"
    assert details[2] == "test@test.com"
    assert bcrypt.checkpw("test".encode("utf-8"), details[3].encode("utf-8"))
    assert details[4] == 1111111111

def test_admin_account_creation():
    assert db._does_admin_exist("test") == False
    success = db.admin_account_creation("test", "test", "test@test.com")
    assert success == True
    assert db._does_admin_exist("test") == True

def test_get_admin_info():
    details = db.get_admin_info(0)
    assert details[0] == 0
    assert details[1] == "test"
    assert bcrypt.checkpw("test".encode("utf-8"), details[2].encode("utf-8"))
    assert details[3] == "test@test.com"

def test_valid_customer_credentials_verification():
    assert db._does_customer_exist("test") 
    assert db.validate_customer_username_password("test", "test")
    assert db.validate_customer_id_password(0, "test")

def test_invalid_customer_password_verification():
    assert db._does_customer_exist("test")
    assert not db.validate_customer_username_password("test", "tesstt")
    assert not db.validate_customer_id_password(0, "tesstt")

def test_valid_admin_password_verification():
    assert db._does_admin_exist("test") 
    assert db.validate_admin_username_password("test", "test")
    assert db.validate_admin_id_password(0, "test")

def test_invalid_admin_password_verification():
    assert db._does_admin_exist("test")
    assert not db.validate_admin_username_password("test", "tesstt")
    assert not db.validate_admin_id_password(0, "tesstt")

def test_insert_new_product():
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

def test_invalid_admin_update_product():
    assert not db.admin_update_product(
        admin_id=0,
        admin_password="bad_password",
        product_id=1,
        new_product_details={
            "price": 9999
        }
    )

def test_admin_update_product():
    assert db.admin_update_product(
        admin_id=0,
        admin_password="test",
        product_id=1,
        new_product_details={
            "price": 9999,
            "stock": 9999,
        }
    )
    product_details = db.retrieve_specific_product_details(product_id=1)
    assert product_details[2] == 9999
    assert product_details[3] == 9999

def test_invalid_admin_remove_product():
    """ensures admin cannot remove product from db if credentials are invalid"""
    assert not db.admin_remove_product(
        admin_id=0,
        admin_password="bad_password",
        product_id=1
    )    
    assert db._does_product_exist(1)

def test_admin_remove_product():
    """ensures admin can remove product from db"""
    assert db.admin_remove_product(
        admin_id=0,
        admin_password="test",
        product_id=1
    )    
    assert not db._does_product_exist(1)

def test_sign_in_customer():
    """ensures valid customer credentials return the correct user id and email"""
    db.customer_account_creation("new_customer1", "test", "test@test.com", "1111111111")
    assert db.sign_in("new_customer1", "test") == (1, "test@test.com")

def test_sign_in_admin():
    """ensures valid admin credentials return the correct user id and email"""
    db.admin_account_creation("new_admin1", "test", "test@test.com")
    assert db.sign_in("new_admin1", "test") == (1, "test@test.com")

def test_sign_in_invalid_customer():
    """ensures invalid customer credentials return None"""
    assert db.sign_in("bad_customer_1", "bad_password_1") is None

def test_sign_in_invalid_admin():
    """ensures invalid admin credentials return None"""
    assert db.sign_in("bad_admin_1", "bad_password_1") is None
    
def test_get_product_categories():
    db.add_product_category("fishing")
    db.add_product_category("food")
    categories = db.get_all_product_categories()
    assert len(categories) == 2
    assert categories[0][0] == "fishing"
    assert categories[1][0] == "food"

    db.set_product_category(1, "fishing")
    assert db.get_product_category(1) == "fishing"

def test_update_product_category():
    db.update_product_category(1, "food")
    assert db.get_product_category(1) == "food"

def test_search_products_by_category():

    db.add_product_category("baseball")

    assert db.admin_add_product(
        admin_id=0,
        admin_password="test",
        product_details={
            "title": "baseball1",
            "price": 100,
            "stock": 100,
            "description": "test",
            "discount_percentage": 10,
            "website_info": "test",
            "date_created": "2025-03-04",
            "product_id": None
        }
    )
    assert db.admin_add_product(
        admin_id=0,
        admin_password="test",
        product_details={
            "title": "baseball2",
            "price": 100,
            "stock": 100,
            "description": "test",
            "discount_percentage": 10,
            "website_info": "test",
            "date_created": "2025-03-04",
            "product_id": None
        }
    )

    assert db.set_product_category(1, "baseball")
    assert db.set_product_category(2, "baseball")

    products_found = db.search_products_by_category("baseball")

    assert len(products_found) == 2
    assert products_found[0] == (1, "baseball1", 100, 100, "test", 10, "test", "2025-03-04")
    assert products_found[1] == (2, "baseball2", 100, 100, "test", 10, "test", "2025-03-04")

def test_search_products_by_name():
    products_found = db.search_products_by_name("baseball1");
    assert len(products_found) == 1
    assert products_found[0] == (1, "baseball1", 100, 100, "test", 10, "test", "2025-03-04")

def test_update_customer_password():
    assert db.update_customer_password(username="test", old_password="test", new_password="test2")
    assert db.validate_customer_username_password("test", "test2")

def test_update_admin_password():
    assert db.update_admin_password(username="test", old_password="test", new_password="test2")
    assert db.validate_admin_username_password("test", "test2")
    
def test_update_customer_email():
    assert db.update_customer_email(customer_id=0, password="test2", new_email="new_email@test.com")
    assert db.get_customer_info(customer_id=0)[2] == "new_email@test.com"

def test_update_admin_email():
    assert db.update_admin_email(admin_id=0, password="test2", new_email="new_email@test.com")
    assert db.get_admin_info(admin_id=0)[3] == "new_email@test.com"