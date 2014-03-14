import subprocess
import datetime
import requests
import json
import globals
import os
import pprint
import re
import sys

# check if files downloadde
with open(globals.json_weekly, "r") as readfile:
    queue_transmission = json.load(readfile)

data_rpc_tg={
        "method":"torrent-get",
        "arguments": {
            "fields": ["id","name","files","status","doneDate"]
            }
        }

data_rpc_tr={
        "method":"torrent-remove",
        "arguments": {
            "ids": [],
            "delete-local-data": True
            }
        }

TR_STATUS_STOPPED        = 0 # /* Torrent is stopped */
TR_STATUS_CHECK_WAIT     = 1 # /* Queued to check files */
TR_STATUS_CHECK          = 2 # /* Checking files */
TR_STATUS_DOWNLOAD_WAIT  = 3 # /* Queued to download */
TR_STATUS_DOWNLOAD       = 4 # /* Downloading */
TR_STATUS_SEED_WAIT      = 5 # /* Queued to seed */
TR_STATUS_SEED           = 6 # /* Seeding */

session = requests.Session()

r1 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc)) #, data=data_rpc)

if r1.status_code == 409:
    header_session_id = {"x-transmission-session-id": r1.headers["x-transmission-session-id"]}
    r2 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc), headers=header_session_id)

# get list from torrent-get for all torrents, then go through 1 by 1, it the torrent is longer than n days, delete it.
r3 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc), headers=header_session_id, data=json.dumps(data_rpc_tg))

r3json = r3.json()

ids = []

if r3json.get("result") == "success":
    for item in r3json["arguments"]["torrents"]:
        done = datetime.datetime.fromtimestamp(item["doneDate"])
        now = datetime.datetime.now()
        diff = now.day - done.day
        diff = now - done
 
        # some title may cause the unicode problem.
        try:
            print item["id"], diff.days, item["status"], item["name"],
        except:
            pass

        if item["status"] == TR_STATUS_SEED and diff.days > globals.max_share_days:
            print ", removed"   
            ids.append(item["id"])

        print "."

    if len(ids) > 0:
        data_rpc_tr["arguments"]["ids"]=ids
        print data_rpc_tr
        r4 = session.post(
                globals.url_rpc, 
                auth=(globals.user_rpc, globals.passwd_rpc), 
                headers=header_session_id, 
                data=json.dumps(data_rpc_tr))
        
        r4json = r4.json()
        pprint.pprint(r4json)

        with open(globals.json_weekly, "w") as writefile:
           json.dump(queue_transmission, writefile, indent=4)
          

