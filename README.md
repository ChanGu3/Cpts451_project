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

# Secret Keys (Environment Variables)
    To keep sensitive information out of the repository (Ex. hashing cookies for session information) we need 
    to create a local shortcut .env file and add the environment variable for secret key,
    
    Like so,
    
    (.env file)
    ```
    SECRET_KEY=your_secret_here
    ```

    This will be your local development key and when we go to deploy we can do the same but actually create the environment variable using bash in the system instead of a local shortcut
    using the same variable name but a special key. (Ex. 'export Secret_Key=Deployment_Key')
