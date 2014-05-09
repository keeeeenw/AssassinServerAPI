# AssassinServerAPI

Provides cloud support for the [Assassin's Game](http://en.wikipedia.org/wiki/Assassin_(game)). Helps players keep track of the progress of the game.

## Architecture

This repository includes the Python-based server engine. The server provides a REST API capable of both GET and POST requests.
The server responds to GET requests with information about player and game status. The server updates data in the database (GAE Datastore) upon receiving POST requests.
All responses from the server are in the JSON format.

## Client Service

The server stores all the user information in a table and manages the login and authorization process.

## Server Development

The server engine uses Python and Flask framework. You need the Google AppEngine SDK to run the server locally or push the engine to production.
Depending on the platform you are using, you can download the corresponding SDK from this link: https://developers.google.com/appengine/downloads.



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


