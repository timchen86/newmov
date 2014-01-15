import requests
import os
from tpb import TPB
from tpb import CATEGORIES, ORDERS
import hashlib
from BeautifulSoup import BeautifulSoup
import re
import json
import sys
import pprint
import globals

url_trakt_signin= "https://trakt.tv/auth/signin"
url_trakt_weekly = "http://trakt.tv/charts/movies" 

#username_trakt = "user"
#password_trakt = "passwd"

#trakt_user = {
#"username":username_trakt,
#"password":password_trakt        
#}


# fresh start 
def get_weekly():
    session_trakt = requests.session()
    #r_trakt_signin = session_trakt.post(url_trakt_signin, data=trakt_user)

    r_trakt_weekly = session_trakt.get(url_trakt_weekly)


    soup = BeautifulSoup(r_trakt_weekly.text)
    soup_items = soup.findAll("div", attrs={"class":"item"})
        
    l_weekly_new = []

    for soup_item in soup_items:
        #span = str(soup_item.findAll("span", attrs={"class":"list add-to-list show-tip"})[0])
        #search_imdb_id = re.search("imdb_id\":\"(.*)\"", span)
        #if search_imdb_id: 
        #    imdb_id = search_imdb_id.group(1)
        #print imdb_id
        ahref = str(soup_item.findAll("a")[1])
        # <a href="/movie/pacific-rim-2013">Pacific Rim  <span 
        # <span class="year">2013</span>
        search_ahref = re.search("href=.*>(.*)<span class=\"year\">(.*)</span", ahref)
        if search_ahref:
            title = search_ahref.group(1).strip()
            year = int(search_ahref.group(2))

        search_rank = soup_item.findAll("div", attrs={"class":"rank inset"})
        rank = int(search_rank[0].text)
        
        item = {
            "type":"movie", 
            "title":title, 
            #"imdb_id":imdb_id, 
            "year":year,
            "rank":rank}
        
        pprint.pprint(item)
        l_weekly_new.append(item)



    with open(globals.json_weekly_temp, "w") as outfile:
        json.dump(l_weekly_new, outfile, indent=4)

    if not os.path.isfile(globals.json_weekly):
        # fresh start
        with open(globals.json_weekly, "w") as outfile:
            json.dump(l_weekly_new, outfile, indent=4)
        print "Found %d new movies" % len(l_weekly_new)
        
    else:
        # merge weekly
        with open(globals.json_weekly, "r") as readfile:
            l_weekly_old = json.load(readfile)
            
            l_delta = []

            for i in l_weekly_new:
                if i["title"] not in [ x["title"] for x in l_weekly_old ]:
                    l_delta.append(i)
                    print "new movie: %s" % i

            l_weekly_new_with_d = l_delta + l_weekly_old

            with open(globals.json_weekly, "w") as outfile:
                json.dump(l_weekly_new_with_d, outfile, indent=4)

            print "Found %d new movies" % len(l_delta)
            return len(l_delta)

if __name__ == "__main__":
    get_weekly()
