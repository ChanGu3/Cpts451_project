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

def test_validate_customer_password():
    db = Database("database.db")
    assert db.customer_account_creation("mark", "password123", "mark@gmail.com", "1111111111")
    assert db.validate_customer_credentials("mark", "password123") == True