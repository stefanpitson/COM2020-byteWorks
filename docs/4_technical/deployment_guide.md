install 

-python 3.14.2

-node js 24.13

-install postgressql 18.1 

&nbsp;	(dont use stack builder)



making postgress db:

open sql shell 

press enter and give the password 

write 'create database byteworks;' 


git clone the repo

add a '.env' file to backend

in the .env file add the line:



DATABASE\_URL=postgresql://postgres:\[password]@localhost/byteworks



\[password] being the password you set for PostgreSQL.



split the terminal:

terminal 1:

cd backend

python -m venv venv

.\\venv\\Scripts\\activate

pip install -r requirements.txt

uvicorn main:app --reload



terminal 2:

cd frontend

npm install

npm run dev



restarting after changes:



in sql shell enter through and give the password

then run:

DROP TABLE IF EXISTS vendor, customer, "user", template, bundle CASCADE;



then 



split the terminal:

terminal 1:

cd backend

.\\venv\\Scripts\\activate

pip install -r requirements.txt

uvicorn main:app --reload



terminal 2:

cd frontend

npm install ?

npm run dev



Common issues:

Having a mac or running Linux:

get a different OS 



npm has security issues:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser



