# Backend Test Instructions

> **Important:** The test scripts must be run from inside the `backend` folder.  
> Function imports only work correctly when executed from this location.
> Ensure that the virtual environment is activated

### Requirements
### Libraries
Run the following comand inside the `tests` directory:

```bash
pip install -r requirements.txt
```

##### .env.test file inside backend/
Contents of .env.test must be:
------------------
HASH_ALGORITHM=256
SECRET KEY= ... 
------------------
SECRET_KEY can be created in the terminal with command: python -c "import secrets; print(secrets.token_urlsafe(32))" 

### Running Tests

Use the following command to run a test:

```bash
python -m pytest -v -s <FULL_PATH_TO_TEST_NAME.PY> -W ignore::DeprecationWarning
```