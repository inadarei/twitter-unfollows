import threading
import twitter
import redis
import sys
import os
import json
from datetime import datetime

def env_var(name, default):
    """Safely retrieve an env var, with a default"""
    return os.environ.get(name) if name in os.environ else default

# this is a pointer to the module object instance itself.
# pylint: disable=invalid-name
this = sys.modules[__name__]

def init():
    REDIS_HOST = env_var("REDIS_HOST", '0.0.0.0')
    REDIS_PORT = env_var("REDIS_PORT", '6379')
    REDIS_DB = env_var("REDIS_DB", '0')
    REDIS_PWD = env_var("REDIS_PWD", '')

    access_token = env_var("TWITTER_ACCESS_TOKEN", "")
    access_token_secret = env_var("TWITTER_ACCESS_TOKEN_SECRET", "")
    consumer_key = env_var("TWITTER_API_KEY", "")
    consumer_secret = env_var("TWITTER_API_SECRET_KEY", "")

    this.redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, \
                              db=REDIS_DB, password=REDIS_PWD,
                              decode_responses=True)

    this.twitter = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token,
                  access_token_secret=access_token_secret,
                  sleep_on_rate_limit=True)

def check():
    print("checking: %s ", str(datetime.now()))
    followers = this.twitter.GetFollowers()
    followers_ids = [follower.id for follower in followers]
    print ("Total of %d followers found", len(followers))

    dictFollowers = {}

    # Add the new followers
    for follower in followers:
    #    print ("[%s] Found a new follower : %s [%s] (#%d)", \
    #         (datetime.today().strftime('%d/%m %H:%M'), follower.name, follower.screen_name, follower.id))

        dictFollowers[follower.id] = str({
                "name": follower.name,
                "screen_name" : follower.screen_name,
                "twitter_id" : follower.id,
                "last" : str(datetime.now())
        })

    unixtimestamp = datetime.now().strftime("%s")
    keyname = "twe" + unixtimestamp
    this.redis_conn.hset(keyname, None, None, dictFollowers)
    this.redis_conn.lpush("twevents", keyname)
    print(f"Added: {keyname}")

def decodeBinaryList(input):
    return [
        el.decode('utf8')
        for el in input
    ]

def formatTwitterUser(twuser):
    # uf = uf.decode('utf-8')
    twuser = json.loads(twuser.replace("'", '"'))
    twuser = {"username" : twuser['screen_name'], "name": twuser['name']}
    return twuser

def printDifferences(tweeps, full_list, none_notice):
    if len(tweeps) > 0:
        diffUsers = [
            formatTwitterUser(el)
            for el in this.redis_conn.hmget(full_list, *tweeps)
        ]
        print(diffUsers)
    else:
        print(none_notice)


def show():
    latest = this.redis_conn.lrange("twevents", 0, 1)
    last = latest[0] #.decode('utf8')
    prelast = latest[1] #.decode('utf8')
    print (f"Latest: {last} - Prelatest: {prelast}")
    kLast = this.redis_conn.hkeys(last)
    kPreLast = this.redis_conn.hkeys(prelast)
    this.redis_conn.sadd("twe-last", *kLast)
    this.redis_conn.sadd("twe-prelast", *kPreLast)

    print("\nChecking new followers...")
    yaydiff = this.redis_conn.sdiff("twe-last", "twe-prelast")
    printDifferences(yaydiff, last, "No new followers in the latest batch")

    print("\nChecking new un-followers...")
    ohdiff = this.redis_conn.sdiff("twe-prelast", "twe-last")
    printDifferences(ohdiff, prelast, "No un-followers in the latest batch")

def scheduler():
    threading.Timer(4.0*3600, scheduler).start()
    check()

def help():
    prefix = f"{sys.argv[0]}"
    print (f"""
Usage:
 {prefix} show - show recent unfollows
 {prefix} run - run the analysis
""")    
    sys.exit(0)

init()
# check()
# scheduler()

if len(sys.argv) != 2:
    help()
if sys.argv[1] != "show" and sys.argv[1] != "run":
    help()

if sys.argv[1] == "show":
    show()
    sys.exit(0)
if sys.argv[1] == "run":
    check()
    sys.exit(0)
