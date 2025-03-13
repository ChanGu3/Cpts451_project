import sys
import os
import sqlite3

"""
This script is used to create a new database.db file.
"""


if __name__ == "__main__":

    # The file path to the test database
    currentWorkingDirectory = os.path.dirname(os.path.abspath(__file__))
    database_filename = "database.db"
    schema_filename = "schema.sql"
    insertions_filename = "insertion_examples.sql"

    # delete old db if exists
    if os.path.exists(database_filename):
        os.remove(database_filename)

    # Connect or create a new test database
    try:
        connection = sqlite3.connect(database_filename)
    except Exception as error:
        os.remove(database_filename)
        print("Error creating database", error)
        exit(1)
        
    # used to execute SQL commands (Acts like the terminal for SQLITE)
    try:
        cursor = connection.cursor()
    except Exception as error:
        connection.close()
        print("Error creating cursor", error)
        exit(1)

    # open file for creating the tables
    with open(schema_filename) as file:
        try:
            cursor.executescript(file.read())
        except Exception as error:
            connection.close()
            os.remove(database_filename)
            print("Error while executing the schema file", error)
            exit(1)

    # close the connection
    connection.close()
    print("test database reset successfully.")


