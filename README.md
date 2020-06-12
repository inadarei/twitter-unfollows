# Twitter Unfollows
Python script helping track unfollows on Twitter

## Prerequisites:

1. Working Docker environment
2. GNU Make
3. Define thw following env variables in your host environment:
      - TWITTER_ACCESS_TOKEN
      - TWITTER_ACCESS_TOKEN_SECRET
      - TWITTER_API_KEY
      - TWITTER_API_SECRET_KEY

## Supported Commands:

1. `make`  - launch redis server and watch logs
2. `make redis-server` - launch redis server
3. `make redis-cli` - launch redis client
4. `make app` - clean rebuild (for extreme debugging)
5. `make check` - Run a Twitter API call for latest data. Can only be done 
6. once n 15 minutes due to Twitter API restrictions
7. `make logs` - tail combined logs from the service and the db
8. `make logs-app`
9.  `make logs-db`
10. `make lint` - pylint code
11. `make test` - run unit and functional tests
12. `make add package="pytest"` - adds a module (in this case: "pytest") inside
a running container and saves it to the requirements.txt.
