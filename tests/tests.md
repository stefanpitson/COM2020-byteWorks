# Backend Test Instructions

> **Important:** The test scripts must be run from inside the `backend` folder.  
> Function imports only work correctly when executed from this location.
> Ensure that the virtual environment is activated

### Requirements
Run the following comand inside the `tests` directory:

```bash
pip install -r requirements.txt
```

Create a .env.test file inside backend/ <br>
Contents of .env.test must be: <br>
HASH_ALGORITHM=256 <br>
SECRET KEY= ... 

SECRET_KEY can be created in the terminal with command: python -c "import secrets; print(secrets.token_urlsafe(32))" 

### Running Tests

Use the following command to run a test:

```bash
python -m pytest -v -s <FULL_PATH_TO_TEST_NAME.PY> -W ignore::DeprecationWarning
```