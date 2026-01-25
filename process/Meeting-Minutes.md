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

project 4 - barcode traceability

project 8 - food waste prevention

### physical notes

![Deciding our project](/pictures/m1-1.jpg "deciding our project")

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
![MoSCoW](/pictures/m2-3.jpg "MoSCoW teirs decided")


# Meeting 3 – 20/01
### Attendance
All but Jack
## Overview
We discussed user stories, establishing their importance and the tasks that need to be accomplished to achieve some of the key parts.
We also planned out some key parts of the design choices, like languages and packages for each part of the project.
Andrew (Technical lead) will establish a skeleton of the project to start Develoupment.
## Scrum Roles:
Product owner - Stefan
Scrum Master - Joe
### Design:
Will use sockets
Front and back will communicate using JSONs passed back and forth between the 2 of them.
#### 2-3 servers:
**DB** - Postgres SQL 
**Back End** - python 
- quicker prototyping 
- fast API over Django flask
	- compile time catching 
	- equal familiarity 
	- data validation is automatic 
	- creates spec automatic spec 

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
We worked through as a team to get everyone's packages and enviroments set up so that we can develop on the skeleton andrew created. 
To summarise:
- install pyrthon 3.14.2, node js latest, postgressql 18
- set up local DB
- create venv 
- start front and backend 
