import sys
import os
import sqlite3

# The file path to the test database
currentWorkingDirectory = os.path.dirname(os.path.abspath(__file__))
database_filename = "test.db"
schema_filename = "schema.sql"
data_inserts_filename = "data-insert.sql"

# Check if the files for execution exist
error_message = "";
if not os.path.exists(f"{currentWorkingDirectory}\\{schema_filename}"):
    error_message += f"[{schema_filename}]"
if not os.path.exists(f"{currentWorkingDirectory}\\{data_inserts_filename}"):
    error_message += f"[{data_inserts_filename}]"   
if error_message != "":
    error_message = f"The following files are missing: {error_message}"
    print(error_message);
    sys.exit(1);

# Delete the test database if it exists for a new testable database
if os.path.exists(f"{currentWorkingDirectory}\\..\\{database_filename}"):
    os.remove(f"{currentWorkingDirectory}\\..\\{database_filename}")

# Connect or create a new test database
try:
    connection = sqlite3.connect(f"{currentWorkingDirectory}\\..\\{database_filename}")
except Exception as error:
    print("Error while connecting to sqlite", error)
    
    
# used to execute SQL commands (Acts like the terminal for SQLITE)
try:
    cursor = connection.cursor()
except Exception as error:
    connection.close()
    os.remove(f"{currentWorkingDirectory}\\..\\{database_filename}")
    print("Error while creating a cursor", error)
    sys.exit(1)

# open file for creating the tables
with open(f"{currentWorkingDirectory}\\{schema_filename}") as file:
    try:
        cursor.executescript(file.read())
    except Exception as error:
        connection.close()
        os.remove(f"{currentWorkingDirectory}\\..\\{database_filename}")
        print("Error while executing the schema file", error)
        sys.exit(1)
        
# open file and insert data into the tables
with open(f"{currentWorkingDirectory}\\{data_inserts_filename}") as file:
    try:
        cursor.executescript(file.read())
    except Exception as error:
        connection.close()
        os.remove(f"{currentWorkingDirectory}\\..\\{database_filename}")
        print("Error while executing the data-insert file", error)
        sys.exit(1)

# close the connection
connection.close()
print("test database reset successfully.")


