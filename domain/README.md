# domain

Domain holds the business logic of Tobias.

## What it does

1. Receives images with some environment information from the UI
2. Sends images to the CV service to get some demographics
3. Forwards demographic information to advertisers
4. Advertisers bid, someone wins
5. Sends winning bid image back to UI for display

## Running it

### Dependencies

* [Leiningen](https://github.com/technomancy/leiningen)
* [Docker](http://docs.docker.com/engine/installation/)

### Steps

Create standard uberjar, build the Docker image, run it like the wind.

