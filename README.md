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

### Tenant tables
The "tenants" table contains all the information about the tenant that we have: it contains all the personnal information and preferences of a tenant, some field were added later when we tried to make a transition to Arthur Online we changed the deposit forms that was in two parts where the tenant has to give more personnal information to match him with other tenants

The "tenant\_history" table is much more complicated to understand: this table contains all the tenancies, therefore every row needs an id of a house ("house\_id"), the id of a tenant ("tenant\_id"), the number of a room ("tenant\_nr") and it needs an incoming date and an outgoing date, a rent and a commitment fees that are all chosen by the agent when he fills a deposit form. All the other fields are needed for the process of the tenancy by our system:

* At first the tenancy is not approved so its "state" is "pending" 
* When the VA's approve the tenancy the "state" switches to "OK" this means that we can send automatically the contracts to this person
* When the contracts are send (which happens automatically one minute after the state is switched to "OK") the field "report_id" is switched to "sent" meaning the contracts are waiting to be signed
* The fields "signature\_rental", "signature\_residential" and "signature\_house" contain the signature for each one of the contract's signature and the "signature" field is filled only when the three signatures are there (use this fact to know where the error happened in the scripts) the "passport" field contains the information about the link of the passport of the tenant that was uploaded with the rental agreement
* We send a copy as a pdf file to the tenants and the "report\_id" field is switched to contain the ids of the google docs that were used to create the contracts
* The "agent" field contains the information about which agent filled the deposit form (good to know who made a mistake) 

### Other tables
Some other tables might need to be mentionned if you want to make use of them



