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
![Database structure](pictures/contracts_process.png?raw=true "Contracts")

This process has been coded excusively on app script you'll find all the codes in the links given in the description of each step (you won't find the code here)

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

### Step 4: The contracts need to be approved by the VAs
In the house confirmation sheet VAs should approve the tenancy to send the contracts by selecting in the last column to confirm the tenancy the information gets back to the database and the tenancy is now confirmed (https://docs.google.com/spreadsheets/d/14fmklWC6jeQllmRPfzWQp75MO8lqsFBSsjtnxkTJeu8/edit?ts=597850d9#gid=1508496129)


### Step 5: Sending the contracts :
The tenancy is now confirmed and we need to send the contracts to the tenants, the script "get_reports_to_send()" does that: it sends the link for the contracts. To trigger it you need to clic on ACTIONS ->  Validate attribution.

### Step 6: Signing the contracts and passport:
This step is performed by the tenant, he is clicking on the link we provided him (it is a link of a get webhook https://script.google.com/a/cocoon.ly/macros/d/MADdHWcEL__3XWUVgmDxCqnevmYI71sMz/edit?uiv=2&mid=ACjPJvGOg7GLYIMzALZqxwdL6YIMVCjysEcMeZjw1e4wYftdopc8oz89TMHawYwVhFJvi1oyXLZKWKkWdxHO6KYCRMFOPRKIfwW6dSzYACDLL-ANrDrtG_WmdkW0oqG90jVDxPk-bZ3S5A ) and the contract is generated on the flight that means it takes the up-to-date information in the database and displays it to the tenant and allows him to sign and upload the passport at the bottom of the contract the signature are stored in the Cloud SQL. Once the three contracts are signed we send a copy to the tenant and that's it (signature_hook https://script.google.com/a/cocoon.ly/macros/d/1aKTx_sGOyw0muU3ynJyYERNXoARbWMRbyPLsu2JwDf4pvR8Si4U2J86y/edit?splash=yes).

## Arthur Process

This process is changing the previous contract process to insure that the process allows to handle the profiles on arthur process. This process replaces step 1, step 2, step 3, step 4 and step 5 of the previous process: the differences are the following ones: the deposit form is changed it's now composed of two part and the confirmation is no done on a spreadsheet but on arthur online. here are the details on how it works exactly. all the code is in the cocoon_app folder in this github all the 

### Step 1: Submitting the deposit form:
it's a similar form like the one described in the previous process (here is the link of the form https://cocoon.formstack.com/forms/new_tenant_copy) however the data is not sent to a app script webhook but it sends the google app engine it sends an email to the tenant to tell him to give us his personal details via another form (please check the main.py file in cocoon/cocoon_app the function associated to '/formstack_deposit' path)

### Step 2: The tenant fills the tenant_information form

The link in the email gives him access to this form (https://cocoon.formstack.com/forms/tenant_information) with a hidden field prefilled that allows us to determine which submission of the deposit form is related to him/her and the information id once again sent to the google app engine to '/formstack_tenant_information' path

### Step 3: Create tenancy on Arthur online and send emails:

The code is still in main.py function whose path is '/formstack_tenant_information'

First we use Formstack's API to get all the data that was submitted in the two previous steps then we use this information to create a tenancy on Arthur Online then use the ID provided on arthur online to create a tenancy in our database (this ID will give our future scripts a way to link the two tenancies, the one in our system and the one in arthur online ) Then we send an email with the information about the prospective tenant to the current tenants

### Step 4: Confirming the tenancy:
The tenancy needs to be confirmed on Arthur online, it is still a manual step, the status of the tenancy needs to be switched from propective to approved. to do so go to the tenancy panel on arthur online, the tenancy should be there with "prospective" as a status, clic on te dropdown arrow on the right of the line

### Step 5: Sending the contracts:
If the process has been undeerstood corectly, the readers should understand that at this moment the tenant was confirmed on arthur online but not in the database (no arthur online doesn't handle events there no point to ask) so we need a process that reguraly checks the status of the tenancy and that checks if any detail has changed. A function handles that in the python wrapper of Arthur's API (cocoon/python\ reboot/arthur.py the same class is coded in the cocoon_app folder and it runs periodically on the google compute engine (cron trigger inscribed in the crontab of the will user) 

### Step 6: Signing the contracts and passport:
This step is the exact same one than in the previous process same functions and same forms



