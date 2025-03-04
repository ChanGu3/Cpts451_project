import pytest
from dbms import Database

def test_new_customer_id():
    db = Database("../database/database.db")
    assert db._new_customer_id() == 0



