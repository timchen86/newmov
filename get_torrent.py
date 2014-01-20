import requests
from tpb import TPB
from tpb import CATEGORIES, ORDERS
import hashlib
from BeautifulSoup import BeautifulSoup
import re
import json
import sys
import pprint
import globals


def get_torrent():
    with open(globals.json_weekly, "r") as readfile:
        l_weekly = json.load(readfile)

    for item in l_weekly:
        #if item.get("torrents"):
        #    continue

        tpb = TPB('https://thepiratebay.org') # create a TPB object with default domain
        # search for 'public domain' in 'movies' category
        search_text = item["title"]+" "+str(item["year"])

        print "*" * 10
        print "Searching for:", search_text
        search = tpb.search(search_text, category=CATEGORIES.VIDEO).order(ORDERS.SEEDERS.DES).page(0)
        

        torrent = [v for i,v in enumerate(search) if i==0]
        
        if len(torrent) < 1:
            continue

        # 1. no torrents retrieved
        # 2. do have torrents and title is different, always get the top rank of torrent
        if (not item.get("torrents")) or \
                (item.get("torrents") and item.get("torrents")[0]["title"] != torrent[0].title):
            item["torrents"] = [
                    {
                        "title":torrent[0].title,
                        "magnet_link":torrent[0].magnet_link,
                        "created":str(torrent[0].created),
                        "size":torrent[0].size,
                        "seeders":torrent[0].seeders,
                        "files":torrent[0].files,
                        "queued":True
                        }
                    ]

            print item["torrents"][0]


    with open(globals.json_weekly, "w") as outfile:
        json.dump(l_weekly, outfile, indent=4)


if __name__ == "__main__":
    get_torrent()
