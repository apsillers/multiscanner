#!/bin/bash

# Run confd to set configuration
confd -onetime -backend env

# Tell Apache to listen on correct port
sed -i -r "s/Listen 80/Listen $MS_API_PORT/" /usr/local/apache2/conf/httpd.conf

# Set CORS regex
#sed -i -r "s;\{\{ ms_api_cors_regex \}\};$MS_API_CORS_REGEX;g" /usr/local/apache2/conf/httpd.conf

# Create sample upload directory
mkdir $MS_UPLOAD_DIR

# Give apache ownership of the multiscanner directory
chown -R daemon:daemon /opt/multiscanner
chown -R daemon:daemon $MS_UPLOAD_DIR

# Run Docker CMD
bash -c "$@"
