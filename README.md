# AssassinServerAPI

Provides cloud support for the [Assassin's Game](http://en.wikipedia.org/wiki/Assassin_(game)). Helps players keep track of the progress of the game.

## Architecture

This repository includes the Python-based server engine. The server provides a REST API capable of both GET and POST requests.
The server responds to GET requests with information about player and game status. The server updates data in the database (GAE Datastore) upon receiving POST requests.
All responses from the server are in the JSON format.

## Client Service

The server stores all the user information in a table and manages the login and authorization process.

## Server Development

The server engine uses Python and Flask framework. You need pip to install the dependencies and you can install pip here: http://pip.readthedocs.org/en/latest/installing.html.
After cloning the project and installing pip, you need to run the following command to install the dependency:

    cd <project-directory>
    pip install -r requirements.txt -t lib

You need the Google AppEngine SDK to run the server locally or push the engine to production.
Depending on the platform you are using, you can download the corresponding SDK from this link: https://developers.google.com/appengine/downloads.

You can deploy the server locally by running:

    python /<GAE-directory>/dev_appserver.py /<project-directory>

You can find the native GAE admin panel by:

    http://localhost:8000

The server automatically seeds players on start-up with username admin and password default. Here are some of the curl requests you can use to see if the server is working.

    curl -X GET http://localhost:8080/api/games
    curl -X GET http://localhost:8080/api/players

