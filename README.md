This utilizes REST APIs that are provided by this repo: https://github.com/GUI/covid-vaccine-spotter

to run just update these fields:
```python
emails = ['receiver_0@gmail.com', 'receiver_1@gmail.com']
SUBJECT = 'subject for email'
# inorder to get gmail to allow sign in. you need to go here: https://myaccount.google.com/
# then security -> and turn on `Less secure app access`
SENDER_EMAIL = "sender@gmail.com" 
SENDER_PASS = 'sender_pass'
RITE_AID = 'Rite Aid'
MY_LOC = (50.000, 50.000) # Longitude , Latitude
MAX_DISTANCE = 10.0 # miles
```

To run this you can just run
```
$ python3 main.py
``

