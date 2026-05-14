#!/usr/bin/python3
'''
Seed the database with 200+ users and 200+ messages each.
Run once: python3 db_seed.py
'''

import hashlib
import random
import sqlite3
from datetime import datetime, timedelta

ADJECTIVES = [
    'happy', 'fast', 'cool', 'bright', 'quiet', 'brave', 'wild', 'silly',
    'clever', 'lazy', 'grumpy', 'jolly', 'spicy', 'fuzzy', 'shiny', 'tiny',
]
NOUNS = [
    'panda', 'rocket', 'cactus', 'wizard', 'falcon', 'otter', 'pixel',
    'noodle', 'koala', 'mango', 'badger', 'cipher', 'walrus', 'llama',
    'goblin', 'narwhal',
]
MESSAGES = [
    'Just had the best coffee of my life.',
    'Does anyone else think about how weird mirrors are?',
    'Today was actually pretty great.',
    'I cannot believe it is already {month}.',
    'Hot take: {food} is overrated.',
    'Just finished reading a great book. 10/10 recommend.',
    'Why is it so hard to find good {thing}?',
    'Shoutout to everyone having a rough day. It gets better.',
    'Check out this cool link: https://en.wikipedia.org/wiki/{topic}',
    'reminder that water is genuinely delicious',
    'anyone else just stare at their screen for 20 minutes doing nothing?',
    'the weather today is {weather}. classic.',
    'I have been thinking about {topic} a lot lately.',
    'pro tip: {tip}',
    'unpopular opinion: {opinion}',
    'just went for a walk and honestly needed that',
    'three things I am grateful for today: coffee, wifi, sleep',
    'my brain is full. no more thoughts today.',
    'woke up and chose productivity. just kidding, I chose snacks.',
    'if you know, you know',
    'some days you are the bug, some days you are the windshield',
    'current mood: {mood}',
    'new personal record: did absolutely nothing for 2 hours straight',
    'lowkey been really into {topic} lately',
    'okay but why does {thing} even work that way',
    'feeling very normal about everything (I am not)',
    'just cleaned my room and now I feel like a different person',
    'the audacity. the nerve. the gall.',
    'it is giving {adjective} vibes today',
    'anyway how is everyone doing',
]
FOODS = ['cereal', 'avocado toast', 'sushi', 'pizza', 'tacos', 'oatmeal']
THINGS = ['parking', 'Wi-Fi', 'good pens', 'sleep', 'chargers']
TOPICS = ['Python', 'space', 'history', 'music', 'mathematics', 'Philosophy', 'Octopus']
TIPS = [
    'always keep a charger with you',
    'drink more water',
    'label your cables',
    'take breaks',
]
OPINIONS = [
    'mornings are fine actually',
    'cold pizza is better than hot pizza',
    'spreadsheets are fun',
    'silence is underrated',
]
MOODS = ['caffeinated', 'chaotic', 'zen', 'feral', 'sleepy', 'determined']
WEATHER = ['incredible', 'suspicious', 'aggressively sunny', 'deeply grey']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


def make_message():
    template = random.choice(MESSAGES)
    return template.format(
        food=random.choice(FOODS),
        thing=random.choice(THINGS),
        topic=random.choice(TOPICS),
        tip=random.choice(TIPS),
        opinion=random.choice(OPINIONS),
        mood=random.choice(MOODS),
        weather=random.choice(WEATHER),
        month=random.choice(MONTHS),
        adjective=random.choice(ADJECTIVES),
    )


def random_timestamp():
    start = datetime(2023, 1, 1)
    end = datetime(2026, 5, 14)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


con = sqlite3.connect('twitter_clone.db')
cur = con.cursor()

# Generate 200 unique usernames
existing = {row[0] for row in cur.execute('SELECT username FROM users')}
new_users = []
seen = set(existing)
while len(new_users) < 200:
    name = random.choice(ADJECTIVES).capitalize() + random.choice(NOUNS).capitalize() + str(random.randint(1, 999))
    if name not in seen:
        seen.add(name)
        new_users.append(name)

cur.executemany(
    'INSERT INTO users (username, password, age) VALUES (?, ?, ?)',
    [(u, hash_password('password'), random.randint(13, 80)) for u in new_users]
)
con.commit()
print(f'Inserted {len(new_users)} users.')

# Get all user IDs for new users
cur.execute('SELECT id FROM users WHERE username IN (%s)' % ','.join('?' * len(new_users)), new_users)
user_ids = [row[0] for row in cur.fetchall()]

# Generate 200 messages per user
messages = []
for uid in user_ids:
    for _ in range(200):
        messages.append((uid, make_message(), random_timestamp().strftime('%Y-%m-%d %H:%M:%S')))

cur.executemany(
    'INSERT INTO messages (sender_id, message, created_at) VALUES (?, ?, ?)',
    messages,
)
con.commit()
print(f'Inserted {len(messages)} messages.')
con.close()
