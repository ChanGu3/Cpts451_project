import os
import sys
project_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_directory)
from backend.dbms import Database # type: ignore (imported using sys.path.append)

def GetDatabase() -> Database:
    database = Database(os.path.join(project_directory, 'backend', 'database.db'))
    return database