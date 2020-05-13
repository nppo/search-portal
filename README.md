Search Portal
=============

A search service for finding open access higher education learning materials.

The repo consists of a frontend and a backend. The frontend is called ``portal`` and is a Vue SPA. 
The backend is named ``service``, which is mostly a REST API, but also serves the frontend SPA and Django admin pages.


Prerequisites
-------------

This project uses ``Python 3.6``, ``npm``, ``Docker`` and ``docker-compose``.
Make sure they are installed on your system before installing the project.


Installation
------------

The local setup is made in such a way that you can run the project inside and outside of containers.
It can be convenient to run some code for inspection outside of containers.
To stay close to the production environment it works well to run the project in containers.
External services like the database run in containers so it's always necessary to use Docker.


#### Backend

To install the backend you'll need to first setup a local environment on a host machine with:

```bash
python3 -m venv venv
source activate.sh
pip install --upgrade pip
pip install -r service/requirements.txt
```

Then copy the ``.env.example`` file to ``.env`` and update the variable values to fit your system.
You'll at least need to provide your Elastic Search credentials and AWS credentials.

If you want to run the project outside of a container you'll also need to add ``POL_DJANGO_POSTGRES_HOST=127.0.0.1``
to the ``.env`` file or add ``127.0.0.1 postgres`` to your hosts file, in order for the service to pickup the database.
Similarly for the Elastic cluster you need to add ``POL_ELASTIC_SEARCH_HOST=127.0.0.1`` to the ``.env`` file
or add ``127.0.0.1 elasticsearch`` to your hosts file.


##### Django setup

After the initial Python/machine setup you can further setup your Django database with the following commands:

```bash
docker-compose -f docker-compose.yml up --build
source activate.sh  # perhaps redundant, already activated above
export DJANGO_POSTGRES_USER=postgres  # the root user who will own all tables
cd service
python manage.py migrate
cd ..
```

This should have setup your database for the most part.
Unfortunately due to historic reasons there is a lot of configuration going on in the database.
So it's wise to get a production dump and import it to your system.
Please ask somebody access to the S3 database dumps bucket. Place the latest dump inside ``postgres/dumps``
and then run:

```bash
make import-db backup=postgres/dumps/<dump-file-name>.sql
```

To finish the Django setup you can create a superuser for yourself using the ``createsuperuser`` command.


##### Elastic Search setup

Similarly to how you can load data into your Postgres database
it's possible to load data into the Elastic Search cluster.
In order to do that you first need to setup with:

```bash
invoke es.setup
```

Backups are stored in a so called repository. You'll need to download the latest ES repository file to load the data.
Ask somebody for the file and name of the latest backup repository and run:

```bash
invoke es.load-repository <repository-file>
invoke es.restore-snapshot <repository-name>
```

This should have loaded the indices you need to make searches locally.
Alternatively you can set the
``POL_ELASTIC_SEARCH_HOST``, ``POL_ELASTIC_SEARCH_PROTOCOL``, ``POL_ELASTIC_SEARCH_USERNAME`` and
``POL_SECRETS_ELASTIC_SEARCH_PASSWORD`` variables inside your ``.env`` file.
This allows to connect your local setup to a remote development or testing cluster.


#### Frontend

Installation of the frontend is a lot more straightforward than the backend:

```bash
cd portal
npm install
```


#### Resetting your database

Sometimes you want to start fresh.
If your database container is not running it's quite easy to throw all data away and create the database from scratch.
To irreversibly destroy your local database with all data run:

```bash
docker volume rm search-portal_postgres_database
```

And then follow the steps above to recreate the database and populate it.


Getting started
---------------

The local setup is made in such a way that you can run the project inside and outside of containers.
External services like the database always run in containers.
Make sure that you're using a terminal that you won't be using for anything else, 
as any containers will print their output to the terminal.
Similar to how the Django developer server prints to the terminal.

> When any containers run you can halt them with ``CTRL+C``.
> To completely stop containers and release resources you'll need to run "stop" or "down" commands.
> As explained below.

With any setup it's always required to use the activate.sh script to **load your environment**.
This takes care of important things like local CORS and database credentials.

```bash
source activate.sh
```

When you've loaded your environment you can choose to only start/stop the database and ES node by using:

```bash
make start-services
make stop-services
```

After that you can start your local Django development server in the ``service`` directory.

Or you can choose to run the entire project in containers with:

```bash
docker-compose up
docker-compose down
```

Either way the Django admin, API and a database admin tool become available under:

```bash
http://localhost:8000/admin/
http://localhost:8000/api/v1/
http://localhost:8081/  # for database administration
```

Last but not least you'll have to start the Vue frontend with:

```bash
cd portal
npm run serve
```

Which makes the frontend available through:

```bash
http://localhost:8080/
```


#### Logging in locally

On the servers the login works through SURFConext.
It's a bit of a hassle to make that work locally.
So we've opted for a way to work around SURFConext when logging in during development.

Simply login to the Django admin.
Once logged in clicking the frontend login button.
This will fetch an API token on Vue servers in development mode and "log you in".
From there on out there is no difference between the remote and local login.


#### Migrate locally

Database tables are owned by the root database user called "postgres".
This is a different user than the application database user.
and that causes problems when you try to migrate,
because the application user is not allowed to alter or create anything.

To apply migrations locally you'll need to switch the connection to the root user.
You can do so by setting an environment variable before running the migration:

```bash
export DJANGO_POSTGRES_USER=postgres
cd service
python manage.py migrate
```


Tests
-----

The test suite is rather limited at the moment. There's not real tests at all for the portal.
However there are some tests for the integration with
the Edurep search engine and our own Elastic Search powered engine.
These engines are what makes the portal tick in the end
and currently you can switch between the two engines with a deploy.
The adapter that connects to these search engines is fully tested.
These tests also assert that the two engines return more or less the same content.
This is to keep the ability to switch engines when needed.

Run these integration tests with the following command:

```bash
make integration-tests
```

