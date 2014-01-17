import subprocess
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
            "fields": ["id","name","files","status"],
            "ids": []
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

cmd_ssh = [
        "/usr/bin/ssh",
        globals.ssh_host,
        "-p",
        globals.ssh_port,
        "" 
        ]

for q in queue_transmission:
    try:
        for t in q.get("torrents"):
            #print t
            if t.get("transmission_id") and t.get("queued"):
                torrent_id = t["transmission_id"]
                data_rpc_tg["arguments"]["ids"] = torrent_id
                print data_rpc_tg
                r3 = session.post(globals.url_rpc, auth=(globals.user_rpc, globals.passwd_rpc), headers=header_session_id, data=json.dumps(data_rpc_tg))
                r3json = r3.json()
                print r3json
                if (r3json.get("result") == "success") \
                        and len(r3json.get("arguments")["torrents"])>0 \
                        and r3json.get("arguments")["torrents"][0]["status"]==TR_STATUS_SEED:
                    # remove the files on 
                    flags_remove = []
                    for f in r3json["arguments"]["torrents"][0]["files"]:
                        check_file = os.path.join(globals.path_trans_lo, f["name"])
                        cmd_ssh[4] = "[ -f \"%s\" ]" % check_file
                        print check_file

                        try:
                            r_ssh = subprocess.check_call(cmd_ssh)
                        except:
                            print "not found"
                            flags_remove.append(False)
                            pass
                        else:
                            print r_ssh
                            flags_remove.append(True)

                    if all(flags_remove):
                        print "ok to remove dir"
                        data_rpc_tr["arguments"]["ids"]=[torrent_id]
                        print data_rpc_tr
                        r4 = session.post(
                                globals.url_rpc, 
                                auth=(globals.user_rpc, globals.passwd_rpc), 
                                headers=header_session_id, 
                                data=json.dumps(data_rpc_tr))
                        
                        r4json = r4.json()
                        pprint.pprint(r4json)
                        t["queued"] = False
    except:
        pass

with open(globals.json_weekly, "w") as writefile:
    json.dump(queue_transmission, writefile, indent=4)



cmd_ssh_file = [
        "/usr/bin/ssh",
        globals.ssh_host, 
        "-p",
        globals.ssh_port,
        "cd %s; find . -type f" % globals.path_trans_lo
        ]
r_ssh = subprocess.check_output(cmd_ssh_file)

l_r_ssh = r_ssh.split("\n")
del(l_r_ssh[-1])

queue_remove_files = []

for r in l_r_ssh:
    re_m = re.match('(?!.*/\..*)', r, flags=re.IGNORECASE)
    if re_m:
        queue_remove_files.append(r)


# full path
queue_remove_files_fp = [ os.path.join(globals.path_trans_remote, f) for f in queue_remove_files ]
#pprint.pprint(queue_remove_files_fp)


for f in queue_remove_files_fp:
    try:
        os.remove(f)
        print "successfully remove %s" % f
    except:
        print "failed to remove %s" % f
        pass

cmd_ssh_dir = [
        "/usr/bin/ssh",
        globals.ssh_host,
        "-p",
        globals.ssh_port,
        "cd %s; find . -type d" % globals.path_trans_lo
        ]

r_ssh_dir = subprocess.check_output(cmd_ssh_dir)

l_r_ssh_dir = r_ssh_dir.split("\n")
del(l_r_ssh_dir[0]) # .
del(l_r_ssh_dir[-1]) # ""

queue_remove_dirs = []
for d in l_r_ssh_dir:
    re_m_dir = re.match('(?!.*/\..*)', d, flags=re.IGNORECASE)
    if re_m_dir:
        queue_remove_dirs.append(d)


queue_remove_dirs_fp = [ os.path.join(globals.path_trans_remote, d) for d in queue_remove_dirs ]
#print queue_remove_dirs_fp

for d in queue_remove_dirs_fp:
    try:
        os.removedirs(d)
        print "successfully remove dir: %s" % d
    except:
        print "failed to remove dir: %s" % d
        pass

