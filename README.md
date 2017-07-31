TITAN
=====

Requirements
---

```
python3
postresql
nginx
```
Install python requirements with `pip install -r requirements.txt`.


Installation
---

    1. Git clone.
    2. Create settings.py file based on settings_dev
    3. Setup and start nginx
   
API    
---   
POST **/api/join/**  - Registers new user without referral code. Email must be sent in request body.  
POST **/api/join/{{CODE}}/** - Registers new user with referral code. Email must be sent in request body.

GET **/api/user/** - Gets currently logged in user data.
GET **/api/user/{{CODE}}/** - Gets user data based on {{CODE}} parameter.
POST **/api/user/{{CODE}}/** - Logs in user with given code. Returns user data
