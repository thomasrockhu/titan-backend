TITAN backend
=====

MVP for user registration and referrals

Requirements
---

```
python3
gunicorn
postgresql
nginx
supervisor
```
Also python requirements can be installed with `pip install -r requirements.txt`.

Installation
---

    1. Git clone
    2. Create settings.py file based on settings_dev.py
    3. Setup environment:
        1. create DB and run migrations
        2. setup supervisor to run gunicorn process
        3. setup nginx
   
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
    wait_list_position:1 (number),
    total_registered: 100 (number)
 } 
 ```

#### Errors


**HTTP 400** if email is not valid
```
{
  "email": [ "Enter a valid email address." ]
}
```

**HTTP 400** if email is not unique
```
{
  "email": [
    "This field must be unique."
  ]
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
    wait_list_position:1 (number),
    total_registered: 100 (number)
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
    wait_list_position:1 (number),
    total_registered: 100 (number)
 } 
 ```

### GET: /api/user/{{CODE}}/ 
Gets user data based on {{CODE}} parameter.


#### Response
 ```
 {
    referral_count: 0 (number),
    referral_code: CODE132 (string),
    wait_list_position:1 (number),
    total_registered: 100 (number)
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
    wait_list_position:1 (number),
    total_registered: 100 (number)
 } 
 ```

#### Errors    
    
**HTTP 404** if user with given code not found


### GET: /api/chart/
Returns data required to draw simple titan/SP-500 chart.

Notes: 

    labels are unix-timestamps in seconds. They can be feed to some date formatter and displayed on chart.
    all samples are ordered from oldest to newest, and groupped by series.
    I.e. it means that:
        labels[0], titan[0] sp500[0] is oldest data we have and represents the same moment in time.
     
 
#### Response
 ```
 {
    labels: [] Array(number),
    titan: [] Array(number),
    sp500: [] Array(number) 
 } 
 ```
  
### GET: /api/stats/
Returns data required to display simple titan/SP-500 statistics.

**Note:** it returns array of objects.
#### Response
 ```
 [{
    label: (text),
    titan: (number),
    sp500: (number) 
 }] 
 ``` 

