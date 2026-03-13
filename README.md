# COM-2020 ByteWork Team Project

This project is an eco-conscious food marketplace web application aimed at preventing food waste by connecting vendors to customers to facilitate the purchase of discounted surplus food bundles.

## Getting Started

The backend code was created on Python version "3.14.2" which can downloaded by clicking [here](https://www.python.org/downloads/release/python-3142/).

Frontend code is written in Typescript and run using Node JS version "24.14" which can be downloaded [here](https://nodejs.org/en/download).

The database is run using PostgreSQL version "18.1" which can be downloaded [here](https://www.postgresql.org/download/).

If you plan on hosting and deploying your own website with the code you will need Docker installed on the host machine, instructions can be found [here](https://docs.docker.com/engine/install/).

Tests were created and run on Python with pytest 9.0.2 as declared in  [requirements.txt](/backend/requirements.txt).

# Running the System

## Accessing Production Environment

This project is self-hosted on a HP Prodesk G2 600 Mini PC using Docker containerisation, Nginx reverse proxy, and a GitHub Runner currently running on a separate private repository.

The main domain [bytework.online](https://bytework.online) is protected by Cloudflare and has a Cloudflare Zero Trust policy attached to it. When accessing the website for the first time or from a new device, please enter your university email ending in '@exeter.ac.uk', Cloudflare will then send you a One-Time Password which will be used to authenticate your browser for 30 days.

## Hosting the website yourself

As stated above we chose to self-host this for our deployment and below we will detail how you can do this yourself:

### Purchasing a domain

Ownership of a valid domain is needed, one year of domain use can be purchased from [porkbun](https://porkbun.com/) or any other domain registrar of your choosing.

### Choosing a reverse proxy

To maintain the security of your home network you should configure a reverse proxy, this will make hosting more accessible (port forwarding and router settings don't need to be configured) and protect against any malicious traffic, AI web scrapers, DDOS attacks etc.
We chose to use [Cloudflare](https://www.cloudflare.com/en-gb/) for this.

Assuming you use a Cloudflare daemon you will need to set up a tunnel in the Zero Trust dashboard under 'Networks -> Connectors'. When you enable a connector via cloudflared you can select which OS you are using (or docker) to get a secure tunnel token, save this somewhere as you may need it later too.  
Ensure when routing the tunnel you enter your domain and route the tunnel to: `http://gateway:80` where gateway refers to the Nginx container defined in docker-compose.yml which serves the frontend.

### Connecting your domain to the reverse proxy

The reverse proxy will provide you with nameservers which need to be pasted into the nameservers input on your domain registrar.

### Deployment Hardware

Once your domain and proxy are linked, you will need to set up hardware to run your webserver, a connector can be set up on Windows, Linux, or Mac. We chose to run ours on Headless Debian-12 Bookworm installation using a HP Prodesk G2 600 Mini PC as stated above with a 500GB HDD and 8GB of DDR4 RAM.

### Running the Server

For this we chose to use a GitHub runner to allow CI/CD via workflows, ensuring that code can deploy before merging to main. You can however also run the repository directly using docker on your host device.

Ensure that Docker and Docker Compose are installed on the host machine using:  
`docker --version`  
`docker compose version`

Before you can run the website you will need to clone the repository to the host device:  
`git clone https://github.com/stefanpitson/COM2020-byteWorks.git`  
And then alter /backend/main.py as follows:  
`origins = ["http://localhost:5173", "http://localhost:3000", "https://bytework.online"] `  
replacing "bytework.online" with your own domain.  

You may also wish to remove these lines in the docker-compose.yml:
```
  tunnel_logs:
    image: cloudflare/cloudflared:latest
    restart: always
    command: tunnel --no-autoupdate --url http://dozzle:8080 run
    environment:
      - TUNNEL_TOKEN=${CF_LOGS_TUNNEL_TOKEN}

  dozzle:
    image: amir20/dozzle:latest
    restart: always
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```
We used dozzle in development to be able to view docker container logs but this is unneeded otherwise.

You will additionally need to configure a .env file in the backend containing the following:

```
POSTGRES_PASSWORD=your_secure_password
CF_TUNNEL_TOKEN=your_saved_tunnel_token
CF_LOGS_TUNNEL_TOKEN=your_logs_token (only add if you are using dozzle, this will also need its own Cloudflare tunnel, same as before)
SECRET_KEY=your_secret_key
HASH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

#### Using docker directly on the host device

From the root directory of the project on the host device, first run:

`docker compose build`

This builds the backend, frontend, database and tunnel images according to the docker-compose.yml file.

To start the containers run:

`docker compose up -d`

If you wish to verify all the containers are running:

`docker ps`

If you have set up cloudflared your website should now be up.

#### GitHub Runner

Should you decide you want to run the website using a GitHub runner instead, you will need to set up your own repository and fork the public repository.
You can store all the .env variables from before in GitHub Secrets and set up a deploy.yml file under .github/workflows/ to launch the website. In GitHub Settings -> Actions -> Runners you can find instructions on how to create and set up a runner on your host device. An example deploy.yml workflow can be found in the branch history of the public byteworks repository.

## Running via Localhost

Please note, the following instructions are for running the project on Windows and some commands may vary if you are on Linux or Mac.

As with running your own deployment you will need to first clone the repository:

`git clone https://github.com/stefanpitson/COM2020-byteWorks.git`

All backend dependencies can be found in [requirements.txt](/backend/requirements.txt) which should be installed before running as detailed below.

Frontend dependencies are included in package.json and installed automatically during runtime.

First you will need to create the database in PostgreSQL, open the SQL Shell and press enter until it prompts you to enter a password and then enter the password you configured when installing PostgreSQL.
Then enter:

`create database byteworks;` 

Next, you will need to create a .env file in the backend as follows:

```
DATABASE_URL=postgresql://postgres:[password]@localhost/byteworks
SECRET_KEY=your_secret_key
HASH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

with [password] being your PostgreSQL password from before.

Finally you will need two terminals open in the directory where you have cloned the repository

Terminal 1:

```
PS C:\COM2020-byteWorks> cd backend
PS C:\COM2020-byteWorks\backend> python -m venv venv
PS C:\COM2020-byteWorks\backend> .\venv\Scripts\Activate
(.venv) PS C:\COM2020-byteWorks\backend> pip install -r requirements.txt
(.venv) PS C:\COM2020-byteWorks\backend> uvicorn main:app --reload
```

Terminal 2:

```
PS C:\COM2020-byteWorks> cd frontend
PS C:\COM2020-byteWorks\frontend> npm install
PS C:\COM2020-byteWorks\frontend> npm run dev
```

Then either click the link given in terminal 2 or navigate to http://localhost:5173/

### Resetting the Database

If you need to reset the database at any point, simply navigate back into the psql shell, enter your password and run the following:

`\c byteworks`  
`DROP TABLE IF EXISTS vendor, customer, "user", template, bundle, reservation, streak CASCADE;`

## Testing

For best results ensure you have already been through the steps outlined in 'Running via Localhost' but stop before starting uvicorn.

At this point you should have installed requirements.txt and activated the venv

You will need to create a new file in the backend called .env.test as follows:

```
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your_secret_key
HASH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

To run the automated tests, run the following command:

`(.venv) PS C:\COM2020-byteWorks\backend> pytest -v ../tests/ -W ignore::DeprecationWarning`

Examples of manual testing are included in testing_evidence.pdf.

## Authors

**Stefan Pitson - Project Lead, Scrum Master, Dev Ops, Frontend Development**  
* Created GitHub Repository, structured Trello board with labels and structured Discord group with various text and voice channels  
* Provisioned hardware and initialised production environment on Debian 12 Bookworm using Docker, Nginx, and Cloudflare for hosting
* Created Customer facing front end pages: CustomerHome.tsx, CustomerVendorView.tsx, CustomerBundleView.tsx, CustomerReservations.tsx
* Created VendorReservations.tsx
* Created all util files in utils folder for frontend efficiency
* Added input validation and errors to Login and Vendor Account Creation Pages
* Structured front end design language and App.css
* Scheduled and led meetings twice a week
* Wrote README.md, deployment_guide.pdf
* Frontend code reviewer
 
**Joe Twiddy - Comms and Documentation, Product Owner, Backend Development**
* Created endpoints for: templates, bundles, streaks 
* Manual API testing 
* Managed creation and structure of documentation
* Wrote meeting minutes for every meeting and added to Figma
* Backend code reviewer
  
**Andrew Tembra - Technical Lead, Frontend Development**  
* Designed and implemented the core full-stack scaffolding and orchestrated installation of all dependencies on developers devices for localhosting
* Created Login.tsx, CustomerSignUp.tsx, VendorSignUp.tsx, VendorDashboard.tsx, VendorAnalytics.tsx
* Created protected route to enforce login
* Created Navbar component
* Created Password hashing and validation utility
* Implemented JWT generation and validation
* Designed and implemented Image upload functionality
* Led technical development of application 
* Frontend and Backend code reviewer

**Magnus Wood - Software Testing Lead, Database Scripting**
* Created Testing framework and automatic tests for all backend files
* Jointly made scripts to seed database with historical data
* Documentation of testing for automatic and manual tests 
  
**Arden Berndt - Data/ML Lead, Documentation, Database Scripting**  
* Created ethical_and_legal_considerations.pdf, licence_decision.pdf, risk_register.pdf, 3rd_party_licenses.md
* Jointly made scripts to seed database with historical data
* Created all forecasting logic and architecture

**Jack Meadows - Backend Development**
* Created all  Reservations endpoints
* Created User and Vendor settings update endpoints
* Added Quality of Life changes and small checks to most of the functions
  
**Alex Thomson - Frontend Development**
* Added input validation to Customer Sign Up
* Created templateDetails.tsx and added input validation
  
**Alfie Morland - Design and Documentation**
* Created Figma
* Created Presentation Slides
* Created Prototype report
 
## License

This program is licensed under the [MIT license](LICENSE.txt), this is contained in full in the file [LICENSE.txt](LICENSE.txt).
