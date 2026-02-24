# Meeting Minutes
# Meeting 1 – 12/01
### Attendance
All present
## Overview

We all discussed the feasibility of each project to decide which we would pick.

Mainly trying to figure the feasibility of the need for APIs.

We have made a Kanban board.

We have made a Git repository.

We also started discussing roles, with some still to be decided.

### Roles

Stephan - project leader

Andrew - Technical lead

Joe - Documentation / Comms

Arden - Data ML lead

Jack - Software Developer

Alex - QA and testing

### Deciding Projects

most likely to choose:

project 4 - barcode traceability: feasibility concerns, getting data for the products may be difficult 

project 8 - food waste prevention: stronger of the 2 as it does not require external information that can be hard to trace. 

### physical notes

![Deciding our project](/pictures/m1-1.png "deciding our project")

# Meeting 2 – 13/01

### Attendance

All but Arden

## Overview

discussing problems, identifying users, and solutions.

We produced a project summary where we discussed what we are building, who it is for, and what problem it solves.

Placing identified issues into MoSCoW tiers.

Finalising the team roles for the start of the project.

### Roles:

Stephan - project leader

Andrew - Technical lead

Joe - Documentation / Comms

Arden - Data ML lead

Jack - Software Developer

Alex - QA and testing

Alfie - Requirements and UX

Magnus - Pen testing/ Dev Ops.

### physical notes

![Users and Problems](/pictures/m2-1.png "Users and problems notes")
![Possible issues to be faced](/pictures/m2-2.png "Possible issues to be faced")
![MoSCoW](/pictures/m2-3.jpg "MoSCoW tiers decided")


# Meeting 3 – 20/01
### Attendance
All but Jack
## Overview
We discussed user stories, establishing their importance and the tasks that need to be accomplished to achieve some of the key parts.
We also planned out some key parts of the design choices, like languages and packages for each part of the project.
Andrew (Technical lead) will establish a skeleton of the project to start Development.
## Scrum Roles:
Product owner - Stefan
Scrum Master - Joe
### Design:
Front and back will communicate using JSONs passed back and forth between the 2 of them.
#### 2-3 servers:
**DB** - Postgres SQL 
**Back End** - python 
- quicker prototyping 
- fast API over Django flask 
	- compile time catching - help prevent bugs
	- equal familiarity - most of the team hasn't worked extensively with either 
	- data validation is automatic - prevent issues with malformed data, preventing issues that might go unnoticed otherwise
	- creates automatic specification/docs - makes it easier for both front end and back end to know what endpoints there are. 

**Front End** - typescript/react framework 
- simple 
- tested 
- shared open api
#### Future Needs for Technical Plan 
ER Diagram 
##### Plan of Web Pages:
-login: required before accessing the website
-landing page 
-Store Page
-Search page for bundles
##### Planning Endpoints:
For each function of the front end there will need to be a corresponding endpoint on the backend, which will actuate the request.
##### Testing:
Mock front and back
Tests needed:
- logins 
- creating bundles 
- reserving bundles 
 
# Meeting 4 - 23/01
### Attendance 
All present, Arden 2 hours late
## Overview 
We worked through as a team to get everyone's packages and environments set up so that we can develop on the skeleton Andrew created. 
To summarise:
- install python 3.14.2, node js latest, postgressql 18
- set up local DB
- create venv 
- start front and backend

#### issues 
This meeting lasted over 3 hours as each individual had different issues that need to be worked through to get all of the packages working, common issues were:
- pip not installing correctly with python
- conflicting versions of python 
- paths not being set properly 
- npm from node needing greater permissions 
- misunderstandings on the postgres installation leading to issues

Individually as well Alex's mac required a very different installation process. 

# Meeting 5 - 26/01
### Attendance
Andrew, Arden, Alex, Stefan, Joe ,Jack

## Overview 
We started work on an Page layout for the design of the front end. 
This can be accessed at:
https://www.figma.com/design/HXzXN460ZO1xMGQeSDfb3Y/group-project?node-id=0-1&p=f

# Meeting 6 - 27/01 
### Attendance 
Andrew, Alfie, Alex, Jack, Joe

## Overview 
We worked on the ER diagram, iterating on the design. Coming to consensus on the basic entities and their attributes, this is still to be hashed out with other team members that were not able to attend.
We also viewed the website designs made by Alfie that will come to guide how each page should look. 

The ER Diagram can be accessed at:
https://lucid.app/lucidchart/9be3478b-b033-4e02-a547-7e9217e29243/edit?invitationId=inv_0d92ce72-aacd-479e-9018-7f7f074c59fe&page=0_0# 

Security and logging-in was discussed, JWT were decided as a way to authenticate users.
## Discussions 
With the expanding understanding of requirements, the stack we plan to use was discussed as maybe too much overhead, that a more simple solution may be better and easier to work with. Concerns were lowered when comparing to other options like flask, or switching languages to java. Discussion highlighted that concerns mainly stemmed from the unfamiliarity, and that with practice it will make more sense. 

Entities for the ER diagram and the database created lots of different opinions, entities like the templates and bundles were considered being merged, similarly badges, forecast entities and others were discussed if necessary.

The proposition of a business entity was heavily discussed, this entity would link different vendors together, and then allow a business wide view of analytics, with the final decision being that this would not be implemented, due to speculated complexity with regards to accounts, and the different analytic views. 

### key decisions
We came to the decision that the search page should feature stores/shops, and that you click-through to view bundles for that particular store/shop. This decision was chosen to manage complexity. Having a page of stores is much easier to create and provides similar level of functionality. 

# Meeting 7 - 30/01
### Attendance 
All present

## Overview 
everyone logged in to the live website 
progress with the website (Andrew) and production server (Stefan) were shown to the group 
We double checked project requirements, making note of any requirements we had not noted 
Discussed log-in pages (do businesses have their own login, if so, how are they verified) ✓ we will have a verify on the admin page 
Discuss individual localhosting, .env file needs to be shared, wiping databases, also command is 'uvicorn main:app --reload --reload-dir app' 
Discuss customer and vendor profiles 
Mention Hashing algorithm decision 
Demonstrate schema changes
Discuss user authentication 
Allocation of new tickets

We discussed how to implement what comes next and planned to individually learn what was there, looking more into the side we were going to be working with. So for frontend the react/node.js, for the backend learning the FastAPI and sqlmodel libraries. 

## assignments 
#### frontend 
Andrew
Stefan
Alex
Alfie 


#### backend
Joe 
Jack 
Magnus 
Arden 

# Meeting 8 - 03/02
### Attendance 
All but Alfie

## Overview
In this meeting Andrew demonstrated the new framework that we will be using for the project, on the back end code is separated into different files to improve organisation, eg. models.py. on the front end demonstrating how to use back end calls and use information from them. 
Andrew also went over the new authentication which will support all of the other end points.

We also began assigning work for individuals to do: 
Andrew - creating vendor sign up 
Alex - verifying user input
Joe - implementing templates and bundles 
Stefan - error messages and refinements
Magnus - testing back end 
Jack - adding customer update endpoint 
Arden - beginning documentation
Alfie - further design work 

# Meeting 9 - 06
### Attendance
All but Alfie and Arden 

## Overview
Due to scheduling issues we had an asynchronous meeting where we discussed specific work we have started and what we are getting on with (1), their progress(2), if we need help with anything(3) and what they are planning to do next (4). This was done over the discord in the meetings channel. 
## Info
#### Andrew:
1-Ive been working on creasing Vendor accounts and uploading their vendor Images
2-I've gotten the functionality implemented and the images can be see in the codebase
3-I would like some help from anyone else in Frontend (Alex/Stefan) to help polish it up, make the colour schemes and style consistent.
4-How that vendors can be created, I would like to work on displaying vendors for the Customer homepage

#### Alex:
1-I'm currently working on the verification of the user inputs for the creating user page
2-I have the verification for all fields not being empty and the length of name to not be longer than 32 charecters working and appearing with red text
3-Not sure if theres anything i really need help with at this moemnt but will update if i do
4-I'll work on polishing up all the screens that have been made to have a consisten colour scheme

#### Joe:
1-Currently working on implementing template and bundle end points.
2-templates are mostly done apart from update, bundles should be relatively quick.
3-No current help needed
4-Reservation end points are next

#### Stefan:
1-currently working on error messages and some refinement of login system
2-have some basic working error messages, going to add protection to the sign in and sign up buttons and password view toggles
3-all good right now
4-will create the first version of the README next

#### Magnus:
1-working on Tests for all the endpoints, including Auth, Customer, Vendor..
2-I've made a local test database that copies the existing model and lives for the duration of the test program, so as of now I am simply creating extensive tests.
3-No help needed, but its on test-main repo, people can simply go into tests directory and make tests easily following the format in the program if needed.
4-Waiting on functional logic to test that is separate from endpoints. Happy to help others if needed!!

#### Jack:
1-On updating customer settings so that customers can change their email, name etc
2-Nearly finished
3-None
4-Work on vendors maybe, or add postcode validation to this function

# Meeting 10 - 10/02
### Attendance 
All but Alfie 

## Overview
We met with the TAs and discussed where the project was at. 
Highlighting the need to beguin creating the documentation, namely:
-prototype report 
-risk register
-ethical and legal considerations 
-deployment guide
-testing evidence 

# Meeting 11 - 13/02
### Attendance
All but Alfie 

## Overview 
We discussed what is left to be implemented for the demo: 
- reservation end points need completing
- pages for customer view of vendors
- pages for vendor home page
- pages for booking bundles 
- pages for collecting bundles

We also discussed what documentation is left to do: 
- prototype report 
- slides for presentation 
- testing report 

planning to work hard over the weekend to have the project ready for the demo

# Meeting 12 - 15/02
## Attendance
All present 

## Overview
We discussed what needs to be implemented before the demo:

#### Endpoints:
- calculate earnings
- streaks 
- basic forecasting 

#### Front end:
- analytics page 
- streaks added to customer nav bar 

### Presentation:
we reviewed the current condition of the presentation and referenced specification to see what needs to be covered.

# Meeting 13 - 16/02
## Attendance
All present 

## Overview
We assigned sections and roles for the presentation and practiced the presentation. 

### Roles 

Alex - click through slides and demo 

Stefan - introduction (30s)

Alfie - explain demo (login + dashboards) (2mins)

Jack - explain demo (ordering + collection codes) (2mins)

Arden - explain demo / analytics plan (explains analytics page) (1min)

Andrew - technical overview (1.5min)

Magnus - testing and evaluation (1min)

Joe - Limitations and Next Steps (1.5mins)

leaving 30 seconds of 'wiggle room' in our 10 minutes. 



# Meeting 14 - 24/06 
## Attendance 
All present

## Overview 
discussed next steps for the project 

### Tasks
Andrew - assist with implementing analytics / user settings page 
Alfie - adding endpoints for badges 
Alex - front end for badges pages
Arden - Review requirements / implementing analytics 
Jack - adding customer credit endpoint / opening times rework 
Stefan - customer credit page 
Joe - rework reservation end point / patch method for vendors 
Magnus - user testing, automated test 

#### Badges
we discussed need for badges, and how we want to implement them: 
- streaks
- first bundles 
- CO2 saved 

#### Leaderboards 
need a leaderboard for customers, details were not discussed

#### admins 
we discussed what is needed, planning one page to start with
other needed functions 
- validate vendors 
- remove bad accounts 
- view all reports 

#### Discussion 
We discussed how we want to implement opening times, and if it should reflect when they close for normal business, or after that time, if we want to add pick up times for a bundle. 
We decided that the alternatives create scope creep and add unnecessary complexity. 

We also discussed a messaging system for customers and vendors, some argued that it could be useful for communicating with the vendor, this was also dismissed as scope creep, and unnecessary when we provide a phone number for the vendor. 