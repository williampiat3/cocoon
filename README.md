# Cocoon documentation
## Introduction
Here is the documentation for all the scripts and all the processes running for cocoon with a description of all the processes running
There are basically two types of processes running on the platform app script processes that are meant to run the old processes and processes running on the google cloud platform.
All the information of the company is stored on the Cloud SQL which is a MySQL database 
I believe the easiest way to introduce you to the structure of all the script perhaps it's easier to introduce you to the data structure first


## Database structure

Here is a picture showing the content of the database:

![Database structure](pictures/DB_structure.png?raw=true "Title")

### Houses tables:
The table "houses" is the one having all the houses and all the details about one house (please see the graph above) all the fields finishing by "\_fid" are ids on formstack, all the other details are informations about the house that need tobe included in every contracts the tenant are signing when they subscribe to a tenancy in a flat. The Id of the house is to be found in a lot of different table

The table "house\_areas" just contains the description of the rooms in one house 

### 

