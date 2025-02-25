# Cpts451_project
WSU Cpts 451 Databases Class Group Project


# Python Virtual Environment Information (Python Version --3.12.9)
    Step 1: Install Python Virtual Environment, |python -m venv .venv
    Step 2: Install Python Library Dependencies (requirments.txt contains all dependancies to install on your own VENV), |pip install -r requirements.txt
                Note: If you install any packages to your environment make sure to overwrite the requirements.txt using |pip freeze > requirements.txt
                        before pushing so everyone can get those dependencies when they merge your work!
    Step 3: Using The Python Environment
        - Windows
            Use the '.venv\bin\Activate.ps1' script (Will see a (.venv) now your in the python virtual environment!)
            TroubleShooting: If AllSIGNED as Execution Policy remove the policy only for the current powershell session by using,
                                |Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    Step 4: Leaving Python Environment, |deactivate

# Secret Keys (Not Sure If We'll need it but most likely)
    Placed In Our Own .env instead of the config.py file so we dont push secret keys to the remote repository