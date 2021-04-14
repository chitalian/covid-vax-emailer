import requests
import json
from geopy.distance import geodesic
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import smtplib, ssl
import copy

emails = ['receiver_0@gmail.com', 'receiver_1@gmail.com']
SUBJECT = 'subject for email'
# inorder to get gmail to allow sign in. you need to go here: https://myaccount.google.com/
# then security -> and turn on `Less secure app access`
SENDER_EMAIL = "sender@gmail.com" 
SENDER_PASS = 'sender_pass'
STATE_CODE = 'CA'
MY_LOC = (50.000, 50.000) # Longitude , Latitude
MAX_DISTANCE = 10.0 # miles


def send_email(subject, body, recipient):
    port = 465  # For SSL

    # Create a secure SSL context
    context = ssl.create_default_context()
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.sendmail(SENDER_EMAIL, recipient, message.as_string())

def send_email_to_all(subject, body):
    print('Sending email to {}\nContent {}'.format(emails, body))
    for e in emails:
        send_email(subject=subject, body=body, recipient=e)
    


def place_distance(place):
    x, y = place['geometry']['coordinates']
    place_coords = (y, x)
    distance = round(geodesic(MY_LOC, place_coords).miles, 2)
    return distance

def place_avail(place):
    return place['properties']['appointments_available'] 

def location_message(place):
    properties = place['properties']
    address = '{}, {}'.format(properties['address'], properties['postal_code'])
    url = properties['url']
    msg = 'There is a new location {} miles away. {}\nsign up here: {}\n'.format(place_distance(place), address, url)
    return msg

def place_name(place):
   return place['properties']['name'] 

def place_id(place):
   return place['properties']['id'] 

def get_places_within(distane):
    r = requests.get('https://www.vaccinespotter.org/api/v0/states/{}.json'.format(STATE_CODE))
    response = json.loads(r.content)
    places = response['features']
    places = [place for place in places if place_avail(place) and place_distance(place) < distane]
    places = sorted(places, key=place_distance)
    return places


previous_places = []

def process_loop():
    global previous_places
    print("Looking for new places")

    places = get_places_within(MAX_DISTANCE)
    prev_ids = [place_id(p) for p in previous_places]
    new_places = [p for p in places if place_id(p) not in prev_ids]

    if new_places:
        print("Found new place(s)!!! :D")
        message = '\n'.join([location_message(place) for place in places])
        print(message)
        lt = time.localtime()
        date_time = '{}/{}/{} @ {}:{}:{}'.format(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_mday, lt.tm_min)
        send_email_to_all(subject="{} {}".format(SUBJECT, date_time), body=message)

    previous_places = copy.deepcopy(places)

while True:
    process_loop()
    time.sleep(2*60)

