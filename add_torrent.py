import pprint
import sys
import json
import requests
import globals

data_rpc={
        "method":"torrent-add",
        "arguments": {
            "filename": "",
            }
        }

def add_torrent():
    session = requests.Session()

    r1 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc)) #, data=data_rpc)

    if r1.status_code == 409:
        header_session_id = {"x-transmission-session-id": r1.headers["x-transmission-session-id"]}
        r2 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc), headers=header_session_id)

    with open(globals.json_weekly, "r") as readfile:
        queue_transmission = json.load(readfile)

    for q in queue_transmission:
        print "Adding: %s ..." % q["title"],
        try:
            for t in q["torrents"]:
                if t.get("queued") and not t.get("transmission_id"):
                    data_rpc["arguments"]["filename"] = t["magnet_link"]
                    r3 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc), headers=header_session_id, data=json.dumps(data_rpc))
                    r3json = r3.json()
                    if r3json["result"] == "success":
                        t["transmission_id"] = r3json["arguments"]["torrent-added"]["id"] 
                        print "ok, id=%d" % t["transmission_id"]
                    
                    if r3json["result"] == "duplicate torrent":
                        print "duplicate torrent"
                else:
                    print "skip"
        except:
            print "skip"
            pass

    with open(globals.json_weekly, "w") as writefile:
        json.dump(queue_transmission, writefile, indent=4)

if __name__ == "__main__":
    add_torrent()
