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
from playsound import playsound
import uuid

# inorder to get gmail to allow sign in. you need to go here: https://myaccount.google.com/
# then security -> and turn on `Less secure app access`
SENDER_EMAIL = "sender@gmail.com" 
SENDER_PASS = 'sender_pass'
CLIENTS = [
    {'id': int(uuid.uuid4()), 'subject': 'Covid update', 'loc': (50.000, 50.000), 'max_distance': 20.0, 'emails': ['client1@gmail.com', 'client1@gmail.com']},
    {'id': int(uuid.uuid4()), 'subject': 'Covid update', 'loc': (50.000, 50.000), 'max_distance': 10.0, 'emails': ['client1@yahoo.com'], 'play_sound': True}
]
SOUND_FILE = '/path/to/sound.wav'
STATE_CODE = 'CA'


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

def send_email_to_all(emails, subject, body):
    print('Sending email to {}'.format(emails))
    for e in emails:
        send_email(subject=subject, body=body, recipient=e)
    
def place_distance(place, client):
    starting_loc = client['loc']
    x, y = place['geometry']['coordinates']
    place_coords = (y, x)
    distance = round(geodesic(starting_loc, place_coords).miles, 2)
    return distance

def place_avail(place):
    return place['properties']['appointments_available'] 

def location_message(place, client):
    properties = place['properties']
    address = '{}, {}'.format(properties['address'], properties['postal_code'])
    city = properties['city']
    url = properties['url']
    msg = 'There is a new location {} miles away in {}. {}\nsign up here: {}\n'.format(place_distance(place, client), city, address, url)
    return msg

def place_name(place):
   return place['properties']['name'] 

def place_id(place):
   return place['properties']['id'] 

def get_places_within(distance, client):
    r = requests.get('https://www.vaccinespotter.org/api/v0/states/{}.json'.format(STATE_CODE))
    response = json.loads(r.content)
    places = response['features']
    places = [place for place in places if place_avail(place) and place_distance(place, client) < distance]
    places = sorted(places, key=lambda x: place_distance(x, client))
    return places


all_places_all_client = {}

def play_alarm():
    for i in range(3):
        sound = SOUND_FILE
        playsound(sound)

def process_loop(client, sound=False):
    global all_places_all_client
    all_places = all_places_all_client.get(client['id'], [])
    print("Looking for new places")
    max_distance = client['max_distance']
    emails = client['emails']
    places = get_places_within(max_distance, client)
    visited_ids = [place_id(p) for p in all_places]
    new_places = [p for p in places if place_id(p) not in visited_ids]

    if new_places:
        print("Found new place(s)!!! :D")
        message = '\n'.join([location_message(place, client) for place in places])
        print(message)
        lt = time.localtime()
        date_time = '{}/{}/{} @ {}:{}:{}'.format(lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_mday, lt.tm_min)
        send_email_to_all(emails, subject="{} {}".format(client['subject'], date_time), body=message)
        if sound:
            play_alarm()
    all_places += new_places

while True:
    for i, client in enumerate(CLIENTS):
        print("Processing client {}".format(i))
        process_loop(client, sound=client.get('play_sound', False))
    time.sleep(2*60)

