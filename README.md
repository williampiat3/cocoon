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

The exact scripts and processes that perform these steps are described later in the documentation

### House reports tables

Another important part of the work was trying to build automatic outgoing and incoming form, sadly due to a poor documentation on the process and an irregular use of the features. Part of the knowledge has been lost this is why I will describe later ohow the sytem works and how this can be changed for the better

The first table that contains all the information about an item is the "items" table: it has information about the location of the item in the house, whose responsibility this item is, a description and an initial state, all the information about the condition of the item can't be stored in tis table because the condition is bound to evolve therefore we need a second table that will register the different states of the item

The second table is called "items\_history" and it contains, as you guessed, the history of the items, it contains information about the tenant that declared the new state of the item and information about the state declared so that the tenant can be contacted if need be. 

### Other tables
Some other tables might need to be mentionned if you want to make use of them

* Tables on minut
Points are devices that were installed in the houses to make sure that tenants don't make too much noise after late hours we store two types of data: sound mesures, pressure, temperature, light and infrarays on a regular basis (every minute) all these informations are on the "minut\_data" table, and we collect also a lot of events: noise level too high, button pressed... in the "minut\_event" table

* Front tables
Contains information about the email we receive on front on specific inboxes for statistics

* Issues table
This table contains the issues that are submitted in the issue form https://cocoon.formstack.com/forms/contact 

* Webhook tokens 
Prototype table to store token for customer application

* Api tokens
Stores all the information about API tokens that we are using for different services like formstack, front, arthur.

* Prospections
It contains the information about the potential future tenants that are sent a message on flatmates.au, it also contains the  information about the tenants that were not matching our criterias (mostly rent criterias)


## Contract process
![Database structure](pictures/contract_process.png?raw=true "Contracts")

### Step 1: Submitting the form
The form to perform this step is the following one:
https://cocoon.formstack.com/forms/new_tenant
You need to fill all the mandatory fields before submitting, becareful the process doesn't accept duplicate sets of first_name,last_name and email. It will reject any attempt to submit duplicates

### Step 2: Automatic treatment of the information
The information is sent to this app script web hook
https://script.google.com/a/cocoon.ly/macros/d/1vPnw2v4QyHcibwwAt9KSxpyTLdaUwgc01QjUOjA6C5CkAAIkGmgm9csf/edit
It formats the information and creates the tenancy and the tenant in the database. The status of the tenancy is "pending"

### Step 3: The information is sent to the the spreadsheet
A script triggered every fifteen minutes by an app script trigger (https://script.google.com/a/cocoon.ly/macros/d/MADdHWcEL__3XWUVgmDxCqnevmYI71sMz/edit look for "upload_signed_contracts()" ) is uploading the pending statuses to the house confirmation sheet Where the VAs can approve a tenancy










