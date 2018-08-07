# Building MutliScanner with Docker Compose #

To deploy distributed MultiScanner using Docker Compose, run

    docker-compose -f docker-compose.dist.yml up

This specifies `docker-compose.dist.yml` as the target Compose configuration file, and runs the `up` command to start the described service.

The Compose config uses the Dockerfiles in `/docker/distributed/` to build the containers for each Multiscanner component (Web interface, REST API, and workers).

## HTTPS Configuration ##

HTTPS can be turned on for the Web interface service and the Web API service. To do so, you will need to

1. Genreate a SSL/TLS certificate (X.509 certificate) and private key for each service that you want to be HTTPS-enabled. How to generate these in general is outside the scope of this setup guide, but to generate a simple self-signed certificate that is valid of one year, you can run the Linux command

        openssl req -x509 -newkey rsa:4096 -keyout msweb.key -out msweb.crt -days 365

    When prompted, enter `msweb` or `msrest` as the entity name. This must match the hostname of the service for which the certificate will be used.

2. In the Compose config file, under the top-level `secrets`, put the file paths to the certificate and key in the `msweb.crt` and `msrest.key` fields (or correspondingly `msrest.crt` and `msrest.key` for the API service).

3. Set `MS_USE_SSL=true` for the service you want to use HTTPS (msweb, msrest, or both). The `true` must be all lowercase.

4. Build and run the Compose services as normal.

## Proxy Configuration ##

If you are building the service behind a proxy, you can uncomment each `-http_proxy` and `-https_proxy` line in the Compose config to inherit your local `http_proxy` and `https_proxy` environment variables.
