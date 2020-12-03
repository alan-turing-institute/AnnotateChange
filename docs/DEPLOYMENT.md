# Notes on Deploying AnnotateChange

Throughout this note we'll use ``YOUR_DOMAIN`` to refer to your base domain 
(i.e. ``gertjanvandenburg.com``) and ``YOUR_EMAIL`` to your email address, 
replace it where mentioned.

## Basics

1. Setup a VPS and go through [My First 5 Minutes on a 
   Server](https://plusbryan.com/my-first-5-minutes-on-a-server-or-essential-security-for-linux-servers)
1. Install Docker using the [instructions available 
   here](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
1. Install docker-compose using [these 
   instructions](https://docs.docker.com/compose/install/)
1. Create a directory for the containers: ``/home/deploy/production``.

## Traefik

We're using [Traefik](https://traefik.io/) to take care of routing the packets 
to the appropriate docker container and taking care of the Let's Encrypt SSL 
certificates. To set up Traefik, follow these steps:

1. Create a directory ``/home/deploy/production/traefik``
1. Add a ``docker-compose.yml`` file with the following content:

   ```yaml
   version: '3'

   services:
     traefik:
       image: traefik
       command: --docker
       container_name: traefik
       ports:
         - 80:80
         - 443:443
       networks:
         - web
       expose:
         - "8080"
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock
         - ./config/traefik.toml:/traefik.toml
         - ./config/acme.json:/acme.json
       labels:
         - "traefik.port=8080"
         - "traefik.frontend.rule=Host:TRAEFIK.YOUR_DOMAIN"
         - "traefik.backend=traefik"
         - "traefik.enable=true"

   networks:
     web:
       external: true
   ```

   Don't forget to change the hostname in the ``traefik.frontend.rule`` line.

1. Create the ``web`` docker network: ``docker network create web``.
1. Create a config directory ``/home/deploy/production/traefik/config``
1. Add a ``traefik.toml`` file with the content:

   ```toml
   debug = false

   logLevel = "INFO"
   defaultEntryPoints = ["https", "http"]

   [entryPoints]
     [entryPoints.http]
     address = ":80"
       [entryPoints.http.redirect]
       entryPoint = "https"

     [entryPoints.https]
     address = ":443"
     [entryPoints.https.tls]

     [entryPoints.api]
     address = ":8080"
       [entryPoints.api.auth]
         [entryPoints.api.auth.basic]
   	users = [
             "YOUR ADMIN PASSWORD"
   	]

   [retry]

   [docker]
   endpoint = "unix:///var/run/docker.sock"
   domain = "YOUR_DOMAIN"
   watch = true
   exposedByDefault = false

   [api]
   entryPoint = "api"
   dashboard = true

   [acme]
   email = "YOUR_EMAIL"
   storage = "acme.json"
   entryPoint = "https"
   onHostRule = true
     [acme.httpChallenge]
     entryPoint = "http"

   [[acme.domains]]
     main = "CHANGE.YOUR_DOMAIN"
   ```
   Create the admin password using ``htpasswd -n admin``.
1. Also, create an empty ``acme.json`` file using ``touch 
   /home/deploy/production/traefik/config/acme.json``.
1. Start the traefik container using ``docker-compose up``. If there are no 
   errors, stop it using Ctrl-C and restart it using ``docker-compose up -d``.

## AnnotateChange

Most of the configuration of the app is provided through environment 
variables, that are encoded in an environment file. An example of such a file 
is included in the Github repository.

1. Create a directory ``/home/deploy/production/annotatechange/``
1. Clone the AnnotateChange repo to this directory and switch to it:
   ```
   $ git clone https://github.com/alan-turing-institute/AnnotateChange /home/deploy/production/annotatechange
   $ cd /home/deploy/production/annotatechange/
   ```
1. Build the docker image:
   ```
   $ docker build -t gjjvdburg/annotatechange .
   ```
1. Copy the ``.env.example`` file to this directory
1. Rename the file ``.env``
1. Update the file for your configuration, at least you'll have to set the 
   ``FLASK_ENV`` to ``production``, set a new ``SECRET_KEY``, configure the 
   mail server and change the ``AC_MYSQL_PASSWORD`` and the 
   ``MYSQL_PASSWORD``. Note that the ``AC_MYSQL_HOST`` variable is set to 
   ``db`` because that is the name in the ``docker-compose.yml`` file.
1. Create a ``docker-compose.yml`` file in this directory with the following 
   content:

   ```yaml
   version: '3'

   services:
     annotatechange:
       image: gjjvdburg/annotatechange:latest
       env_file: .env
       labels:
         - "traefik.backend=annotatechange"
         - "traefik.docker.network=web"
         - "traefik.frontend.rule=Host:CHANGE.YOUR_DOMAIN"
         - "traefik.port=7831"
       networks:
         - internal
         - web
       depends_on:
         - db
       volumes:
         - ./persist/instance:/home/annotatechange/instance

     db:
       image: mysql
       env_file: .env
       volumes:
         - ./persist/mysql:/var/lib/mysql
       networks:
         - internal
       labels:
         - "traefik.enable=false"

   networks:
     web:
       external: true
     internal:
       external: false
   ```

1. To achieve persistent storage and correct permissions for the docker 
   volumes, create a ``persist`` directory and use the following commands:

   ```
   $ mkdir persist/{instance,mysql}
   $ sudo chown :1024 persist/instance
   $ chmod 775 persist/instance
   $ chmod g+s persist/instance
   ```
1. Now you should be able to start the application using ``docker-compose 
   up``. If there are no errors, stop it using Ctrl+C and restart using 
   ``docker-compose up -d``.
