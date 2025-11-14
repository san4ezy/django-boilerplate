This is the powerful boilerplate for Django+RestFramework projects.

It contains all basic configuration, multiple environment settings, dockerized environment, JWT authorization, customizable User model and lots of sugar.

Start it in 5 minutes.

Before you start, you should have installed Docker and Docker Compose, Python (of course) and installed globally Fabric.

## Installation

By default, we use Postgres as the database for the project. 

Pull this repo, create a basic env file from the template and modify it on your taste:

```bash
cp .env.example .env
```
- **ENV** -- The name of environment you want to install. Choose one: development, staging, production. 
- **PROJECT_NAME** -- This name will be used as the prefix for all containers.
- **APP_NAME** -- Desired name of the main Django app.
- **APP_PORT** -- Port, where Django will be located.
- **COMPOSE_PROJECT_NAME** -- The name used for the Compose entities.

Now we need to generate environment files and data: 
```bash
fab setup
fab keygen
```
First one makes a copies of all needed files and locate them at the `environments/<ENV>` directory.
Second one generates all secret keys for Django, Simple JWT and token payload.
Of course, you can modify this data manually. But notice, if you already have image build you need to rebuild it again every time you change something here.

Now the boilerplate is available for up:
```bash
fab docker build
fab docker up
fab dj migrate
```

Optionally, create an admin:
```bash
fab dj createsuperuser
```

Now you have Django running with Docker on defined port.

## Commands

Pls, explore the `fabfile.py` content to know other commands.

Here collected most popular commands with potential needed options for run them fast with a short single Fabric command.

Feel free to extend this list with your commands.

- **fab setup** -- Setup new environments. Be careful, it will replace existing env files and compose files. Use it if you want setup new environment, changing the `ENV` variable first.
- **fab keygen** -- Generate random secret keys and write them to `environments/<ENV>/app.env` file
- **fab docker build** -- Initiate the compose build process
- **fab docker rebuild** -- Down existing project, build it and up again
- **fab docker up** -- Just up project
- **fab docker down** -- Just down project
- **fab docker ps** -- List running containers
- **fab docker logs** -- Tail logs of the Django app
- **fab docker start** -- Start project
- **fab docker stop** -- Stop Project
- **fab docker restart** -- Restart project
- **fab docker bash** -- Run Django container's bash
- **fab dj shell** -- Run Django shell
- **fab dj makemigrations/migrate/showmigrations** -- Run Django migrations commands
- **fab dj collectstatic** -- Run Django collect static command
- **fab dj createsuperuser** -- Start the superuser creation flow
- **fab dj startapp** -- Create new Django application

Some commands have default args values. But you can impact how it works. For example:
```bash
fab docker logs
# docker compose -f environments/development/docker-compose.yml logs app --tail 100 -f
fab docker logs --args '--tail 1000'
# docker compose -f environments/development/docker-compose.yml logs app --tail 1000
```

## New application

If you need to start new Django app, you can do it fast: `fab dj startapp`. It generates new app placed at the needed folder.
