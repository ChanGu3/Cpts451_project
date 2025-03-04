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