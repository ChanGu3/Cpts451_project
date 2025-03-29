import sys
import os
import sqlite3

# The file path to the test database
currentWorkingDirectory = os.path.dirname(os.path.abspath(__file__))
backendDirectory = os.path.join(currentWorkingDirectory, "..", "backend")
database_filename = "test.db"
schema_filename = "schema.sql"
data_inserts_filename = "data-insert.sql"

# Check if the files for execution exist
error_message = ""
# Use os.path.join to ensure correct file paths for the OS
if not os.path.exists(os.path.join(backendDirectory, schema_filename)):
    error_message += f"[{schema_filename}]"
if not os.path.exists(os.path.join(currentWorkingDirectory, data_inserts_filename)):
    error_message += f"[{data_inserts_filename}]"
if error_message != "":
    error_message = f"The following files are missing: {error_message}"
    print(error_message)
    sys.exit(1)

# Delete the test database if it exists for a new testable database
# The path should also be constructed using os.path.join
if os.path.exists(os.path.join(currentWorkingDirectory, database_filename)):
    os.remove(os.path.join(currentWorkingDirectory, database_filename))

# Connect or create a new test database
try:
    connection = sqlite3.connect(os.path.join(currentWorkingDirectory, database_filename))
except Exception as error:
    print("Error while connecting to sqlite", error)

# Used to execute SQL commands (Acts like the terminal for SQLITE)
try:
    cursor = connection.cursor()
except Exception as error:
    connection.close()
    os.remove(os.path.join(currentWorkingDirectory, database_filename))
    print("Error while creating a cursor", error)
    sys.exit(1)

# Open file for creating the tables
try:
    with open(os.path.join(backendDirectory, schema_filename)) as file:
        cursor.executescript(file.read())
except Exception as error:
    connection.close()
    os.remove(os.path.join(currentWorkingDirectory, database_filename))
    print("Error while executing the schema file", error)
    sys.exit(1)

# Open file and insert data into the tables
try:
    with open(os.path.join(currentWorkingDirectory, data_inserts_filename)) as file:
        cursor.executescript(file.read())
except Exception as error:
    connection.close()
    os.remove(os.path.join(currentWorkingDirectory, database_filename))
    print("Error while executing the data-insert file", error)
    sys.exit(1)

# Close the connection
connection.close()
print("Test database reset successfully.")


