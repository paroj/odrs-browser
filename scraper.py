# @author Pavel Rojtberg
# SPDX-License-Identifier: AGPL-3.0-or-later

import urllib.request
import urllib.parse
import json
import hashlib
import time

review_server = "https://odrs.gnome.org/1.0/reviews/api"
# /ratings
# /fetch

CONTINUE=0 # set to number of apps that were already fetched

locales = ["en", "de", "es", "fr", "ru", "zh"]

def fetch_ratings():
    res = urllib.request.urlopen(review_server+"/ratings").read()
    ratings = json.loads(res.decode("utf-8"))
    open("data/ratings.json", "w").write(json.dumps(ratings))
    return ratings

def fetch_reviews(appid):
    data = {
        "user_hash" : hashlib.sha1(b"").hexdigest(),
        "app_id" : appid,
        "locale" : "en",
        "distro" : "Ubuntu",
        "version" : "unknown",
        "limit" : 100
    }

    reviews = []

    for loc in locales:
        data["locale"] = loc
        req = urllib.request.Request(review_server+"/fetch", headers = {'Content-Type': 'application/json'})
        ntries = 2
        while ntries > 0:
            try:
                res = urllib.request.urlopen(req, data=json.dumps(data).encode()).read()
                break
            except urllib.error.HTTPError as e:
                print(e, ", RETRYING")
                ntries -= 1
                time.sleep(1)
        

        if b"summary" not in res:
            continue
        
        lreviews = json.loads(res.decode("utf-8"))

        for r in lreviews:
            r.pop("user_hash", None)
            r.pop("user_skey", None)

        reviews += lreviews

    open("data/"+appid+".json", "w").write(json.dumps(reviews))

if CONTINUE:
    ratings = json.loads(open("data/ratings.json").read())
else:
    ratings = fetch_ratings()

for i, appid in enumerate(ratings.keys()):
    if i < CONTINUE:
        continue
    print(appid, i, "/", len(ratings))
    fetch_reviews(appid)
