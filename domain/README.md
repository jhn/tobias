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

1. Create uberjar

    lein uberjar

2. Build Docker image

    docker build -t tobias .

3. Run image

    docker run \
      -d              # as daemon
      -p 80:3000 \    # internet:jetty
      -p 3001:3001 \  # internet:nrepl
      --name tobias   # container name
      tobias          # our image

If running somewhere else, before running the image either:

1. Push Tobias to a Docker registry
2. Pull Tobias from the registry

Or

1. Save image as tar

    docker save -o tobias.tar tobias

2. Copy image to target server

    scp tobias.tar user@host:path

3. Load image in target

    docker load -i tobias.tar

