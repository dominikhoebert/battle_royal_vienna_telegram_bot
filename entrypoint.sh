#!/bin/bash

# Copy the file to the mounted volume if it doesn't already exist
if [ ! -f /bot/data/maps.csv ]; then
  cp /bot/origin/maps.csv /bot/data/
fi

if [ ! -f /bot/data/poi.csv ]; then
  cp /bot/origin/poi.csv /bot/data/
fi

if [ ! -f /bot/data/secrets.json ]; then
  cp /bot/origin/secrets.json /bot/data/
fi

if [ ! -f /bot/data/test.yml ]; then
  cp /bot/origin/test.yml /bot/data/
fi

if [ ! -f /bot/data/1bezirk.yml ]; then
  cp /bot/origin/1bezirk.yml /bot/data/
fi

# Execute the passed CMD
exec "$@"
