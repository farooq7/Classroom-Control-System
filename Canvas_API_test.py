import requests
import json


access_token = '4511~GQcH0fUmjvtRoFawOBpCSmRyMM9mG3JwG6VS8MuczKlPfVO298Tl0iOSl8cmiCG6'
api_url = 'https://canvas.vt.edu/api/v1/groups/52704/files'

# Set up a session
session = requests.Session()
session.headers = {'Authorization': 'Bearer %s' % access_token}

down_url = 'https://canvas.vt.edu/api/v1/groups/52704/files'
r = session.get(down_url)
r.raise_for_status()
r = r.json()
len = len(r)
for i in range(0, len):
    if(r[i]["filename"] == 'dict_mac.py'):
        down_url += '/'
        down_url += str(r[i]["id"])
        down2_url = str(r[i]["url"])

r = session.get(down_url)
r.raise_for_status()
r = r.json()
r = session.get(down2_url)
r.raise_for_status()
t = r.content.decode("ascii")
t2 = json.loads(t)
print(t2)