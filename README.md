Search Portal
=============

Search service for finding open access higher education learning materials.

The repo consists of a frontend, a backend and a background task component.
The frontend is called ``portal`` and is a Vue SPA.
The backend is named ``service``, which is mostly a REST API, but also serves the frontend SPA and Django admin pages.
Background tasks are handled by a Celery Django app named ``harvester``,
but there is also an admin available for that part.


Prerequisites
-------------

This project uses ``Python 3.6``, ``npm``, ``Docker``, ``docker-compose``, ``psql`` and ``chromedriver``.
Make sure they are installed on your system before installing the project.


Installation
------------

The local setup is made in such a way that you can run the project inside and outside of containers.
It can be convenient to run some code for inspection outside of containers.
To stay close to the production environment it works well to run the project in containers.
External services like the database run in containers, so it's always necessary to use Docker.


#### General setup

To install the basic environment and tooling you'll need to first setup a local environment on a host machine with:

```bash
python3 -m venv venv
source activate.sh
pip install --upgrade pip
pip install -r requirements.txt
```

Then copy the ``.env.example`` file to ``.env`` and update the variable values to fit your system.
For a start the default values will do.

If you want to run the project outside of a container you'll need to add ``POL_DJANGO_POSTGRES_HOST=127.0.0.1``
to the ``.env`` file or add ``127.0.0.1 postgres`` to your hosts file, in order for the service to pickup the database.
Similarly for the Elastic cluster you need to add ``POL_ELASTIC_SEARCH_HOST=127.0.0.1`` to the ``.env`` file
or add ``127.0.0.1 elasticsearch`` to your hosts file.

To finish the general setup you can run these commands to build all containers:

```bash
invoke prepare-builds
docker-compose -f docker-compose.yml up --build
```


Getting started
---------------

The local setup is made in such a way that you can run the components of the project inside and outside of containers.
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

After that you can follow the guides to [start the service](service/README.md),
[work with the frontend](portal/README.md) or [start the harvester](harvester/README.md).
Alternatively you can choose to run all components of the project in containers with:

```bash
docker-compose up
docker-compose down
```


#### Available apps

Either way the database admin tool become available under:

```bash
http://localhost:8081/
```


#### Resetting your database

Sometimes you want to start fresh.
If your database container is not running it's quite easy to throw all data away and create the database from scratch.
To irreversibly destroy your local database with all data run:

```bash
docker volume rm search-portal_postgres_database
```

And then follow the steps to [install the service](service/README.md#installation) and
[install the harvester](harvester/README.md#installation) to recreate the databases and populate them.


Tests
-----

You can run all tests for the entire repo (except external Elastic Search integration) by running:

```bash
invoke test.run
```

It's also possible to run tests for specific Django projects.
For more details see: [testing service project](service/README.md#tests) and
[testing harvester project](harvester/README.md#tests)

To see whether the code integrates correctly with the external Elastic Search service run:

```bash
invoke test.elastic_search
```


Deploy
------

This section outlines the most common options for deployment.
Use ``invoke -h <command>`` to learn more about any invoke command.

Once your tests pass you can make a new build for the project you want to deploy:

```bash
invoke aws.build <target-project-name>
```

After you have created the image you can push it to AWS.
This command will push to a registry that's available to all environments on AWS:

```bash
invoke aws.push <target-project-name>
```

When an image is pushed to the registry you can deploy the service with:

```bash
APPLICATION_MODE=<environment> invoke srv.deploy <environment>
```

And the harvester with:

```bash
APPLICATION_MODE=<environment> invoke hrv.deploy <environment>
```


#### Rollback

In order to rollback you can specify an existing Docker image to deploy command.
For instance with the service:

```bash
APPLICATION_MODE=<environment> invoke srv.deploy <environment> -v <rollback-version>
```


#### Migrate

To migrate the database on AWS you can run the migration command:

```bash
APPLICATION_MODE=<environment> invoke migrate <target-project-name> <environment>
```


Provisioning
------------

There are a few commands that can help to provision things like the database on AWS.
We're using Fabric for provisioning.
You can run ``fab -h <command>`` to learn more about a particular Fabric command

For more details on how to provision things on AWS see [provisioning the service](service/README.md#provisioning) and
[provisioning the harvester](harvester/README.md#provisioning)


Linting
-------

The python code uses flake8 as a linter. You can run it with the following command:

```bash
flake8 .
```
