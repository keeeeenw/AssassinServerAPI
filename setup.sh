#!/bin/bash

# download the dependency packages

if [ ! -f /lib ]
    then
    mkdir lib
fi

mkdir lib/tmp
git clone https://github.com/kamalgill/flask-appengine-template.git lib/tmp/sample
cp -r lib/tmp/sample/src/lib .