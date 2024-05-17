import requests
import time
import json
from threading import Timer

HYPIXEL_API_KEY = ""
DISCORD_WEBHOOK_URL = ""
CHECK_INTERVAL = 60 * 5  # 5 minutes
WARN_AFTER = 60 * 60 * 9  # 9 hours

profiles = [
    {
        "profile": "",
        "playerId": "",
        "ping": "",
    },
]

lastCollectionGain = [0] * len(profiles)
lastCollection = [0] * len(profiles)


def get_profile(p):
    url = f"https://api.hypixel.net/v2/skyblock/profiles?key={HYPIXEL_API_KEY}&uuid={p['playerId']}"
    response = requests.get(url)
    data = response.json()
    return next((profile for profile in data['profiles'] if profile['cute_name'] == p['profile']), None)


def warn(userid):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "content": f"<@{userid}> RATE MAL WER GERADE KEINE MYCELIUM COLLECTION BEKOMMT? DU!",
        "allowed_mentions": {
            "users": [userid],
        },
    }
    response = requests.post(DISCORD_WEBHOOK_URL + "?wait=true", headers=headers, data=json.dumps(payload))
    return response.json()


def check_collections():
    global lastCollectionGain, lastCollection

    for i, p in enumerate(profiles):
        data = get_profile(p)
        if not data:
            continue

        collection_total = sum(member.get('collection', {}).get('MYCEL', 0) for member in data['members'].values())

        last = lastCollection[i]
        if last != collection_total:
            lastCollection[i] = collection_total
            lastCollectionGain[i] = time.time()

        if time.time() - lastCollectionGain[i] > WARN_AFTER:
            response = warn(p['ping'])
            print(response)

        print(f"last: {last}")
        print(f"current: {collection_total}")

    Timer(CHECK_INTERVAL, check_collections).start()

# Initial call to start the checking loop
check_collections()
