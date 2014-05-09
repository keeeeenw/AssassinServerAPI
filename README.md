# AssassinServerAPI

Provides cloud support for the [Assassin's Game](http://en.wikipedia.org/wiki/Assassin_(game)).

Testing Server Side API using Flask Framework for Assassin App

(1) Which tutorials and resources you used?

Google AppEngine Tutorial:

https://developers.google.com/appengine/ 

Flask Tutorial: 

http://flask.pocoo.org/docs/tutorial/

(2) What your code does?

1. You can login using username 'admin' and password 'default' to add new games and view current games

2. User call the server API, the server returns the content of Game model as JSON.

 You can access the API using "http://127.0.0.1:5000/api/list\_games if you are logged in.

 You could also use http://127.0.0.1:5000/api/list\_games?dev\_key=t6ra1M77Ei80b35LeV5I55EN7c
if you do not want to log into the application

3. The app is working on Google App Engine

http://macassassingame.appspot.com
http://www.raymondcamden.com/index.cfm/2012/6/21/Update-to-my-ServerBased-Login-PhoneGap-Demo


# Snow Alerts

Provides information and notifications for special winter parking rules. Currently supports only the city of Minneapolis.

## Architecture

This repository includes both the iOS client and the Ruby-based server engine. The server provides a read-only REST API which provides details of the parking rules currently in effect. Because this API is read-only, the server code does not respond directly to requests; instead, it generates pre-baked JSON files which Apache serves directly from the file system.

The engine scrapes the City of Minneapolisâ€™s public web site to see if a snow emergency is in effect, and if so, generates a parking rule timeline based on the configuration in `server/config/cities`.

We use Urban Airship to send push notifications.

Scraping, API file generation, and notification queueing are all triggered by a cron job on the server.

[<img src="doc/Architecture.png" width="652" height="483">](doc/Architecture.pdf)

## Client Development

The iOS client is a standard XCode 5 project, targeting iOS 7.

To facilitate testing with fake snow emergencies, the app uses fake data in development builds by default. When launched in the simulator, the app loads the rule JSON from a local file whose path is hard-coded in `SnowRuleSet.m`. When launched on a device, both developer builds and ad hoc (i.e. beta) builds will ask the server for `minneapolis-dev.json` instead of `minneapolis.json`. In dev and ad hoc builds, you can toggle between production data and fake data by quintuple-tapping the nav bar of the main view controller.

## Server Development

The server engine uses Ruby. Be sure you have rvm or rbenv installed, so that the `.ruby-version` file takes effect. To configure:

    cd server
    gem install bundler  # if not already installed
    bundle

To run the regression tests:

    rake test

You can also run `guard` to automatically rerun tests when files are modified.

To declare a test snow emergency:

    bin/snow-alerts declare minneapolis snow_emergency start_time=2014-5-6

Generated files go in `server/work/`. This includes both JSON files and the SQLite database the engine uses to track state between calls. (Note that the script automatically creates and migrates the database, so you do not need to install or configure a DB yourself.)

To send any pending â€œmove your carâ€ notifications (requires valid config in `server/config/urbanairship.yml`):

    bin/snow-alerts notify

To clear all emergencies and start over:

    rm work/alerts.db
    bin/snow-alerts generate

Run the `snow-alerts` script with no args for help.

