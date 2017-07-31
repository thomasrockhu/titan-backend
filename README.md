TITAN backend
=====

MVP for user registration and referrals

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
### POST: /api/join/  

Registers new user without referral code. 
Email must be sent in request body.

#### Body
 ```
 { 
    'email' : 'valid@email.com' 
 }
 ```

#### Response
 ```
 {
    referral_count: 0 (number),
    referral_code: CODE132 (string),
    wait_list_position = 1 (number) 
 } 
 ```

#### Errors


**HTTP 400** if email is not valid
```
{
  "email": [ "Enter a valid email address." ]
}
```
  
### POST: /api/join/{{CODE}}/ 
Registers new user with referral code. 
Email must be sent in request body.

#### Body
 ```
 { 
    'email' : 'valid@email.com' 
 }
 ```
 
 
#### Response
 ```
 {
    referral_count: 0 (number),
    referral_code: CODE132 (string),
    wait_list_position = 1 (number) 
 } 
 ```

#### Errors

**HTTP 404** if user with given code not found
    
**HTTP 400** if email is not valid
```
{
  "email": [ "Enter a valid email address." ]
}
```

### GET: /api/user/
Gets currently logged in user data.


#### Response
 ```
 {
    referral_count: 0 (number),
    referral_code: CODE132 (string),
    wait_list_position = 1 (number) 
 } 
 ```

### GET: /api/user/{{CODE}}/ 
Gets user data based on {{CODE}} parameter.


#### Response
 ```
 {
    referral_count: 0 (number),
    referral_code: CODE132 (string),
    wait_list_position = 1 (number) 
 } 
 ```

#### Errors

**HTTP 404** if user with given code not found
    
    

### POST: /api/user/{{CODE}}/ 
Logs in user with given code. Returns user data


#### Response
 ```
 {
    referral_count: 0 (number),
    referral_code: CODE132 (string),
    wait_list_position = 1 (number) 
 } 
 ```

#### Errors    
    
**HTTP 404** if user with given code not found
