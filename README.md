# Django Docker SaaS Starter

## Get Started For IDE

### Prerequisites

- git >= 2.32.1
- python >= 3.11.0
- npm >= 8.11.0
- node >= 17.9.0

### Setting Up the Environment for Development

Homebrew

```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew update
```

Virtual Environments

```sh
# Download Repository
git clone [repository]
cd [repository]

# Creating Virtual Environments
python3 -m venv venv
source venv/bin/activate
```

Coding Style Standard

```sh
# The uncompromising Python code formatter.
brew install black
```

Recommended Setting for VS Code

```sh
# IntelliSense (Pylance), Linting, Debugging (multi-threaded, remote),
# Jupyter Notebooks, code formatting, refactoring, unit tests, and more.
ext install ms-python.python

# Markdown linting and style checking for Visual Studio Code
ext install markdownlint

# Visual Studio Code extension to prettify markdown tables.
ext install markdown-table-prettify
```

Git Commit Message

```sh
# commitlint
npm install
npx husky install
chmod a+x .husky/commit-msg
```

Pre Commit

```sh
# pre-commit

# Install the git hook scripts
pre-commit install

# Run against all the files
pre-commit run --all-files
```

## Building Up the Project for Development

### Install Docker

```sh
# Docker
brew install docker docker-compose
open /Applications/Docker.app
```

### Customize the Settings

```sh
# Create custom setting
cp app/.env.example app/.env.local
vi app/.env.local
cp docker-compose.example.yml docker-compose.local.yml
vi docker-compose.local.yml
```

### Build images, Start containers

```sh
# Build images, Start containers
docker-compose -f docker-compose.local.yml up -d --remove-orphans --build
```

### Some Routine Actions

```sh
# Django CLI
docker-compose -f docker-compose.local.yml exec web python manage.py shell

# Flush database
docker-compose -f docker-compose.local.yml exec web python manage.py flush

# PostgreSQL CLI
docker-compose -f docker-compose.local.yml exec web python manage.py dbshell
docker-compose -f docker-compose.local.yml exec db psql -d postgres_local -U postgres

# Stops containers and removes containers
docker-compose -f docker-compose.local.yml down

# Stops running containers without removing them
docker-compose -f docker-compose.local.yml stop

# Starts existing containers for a service
docker-compose -f docker-compose.local.yml start

# Restarts all stopped and running services
docker-compose -f docker-compose.local.yml restart

# Displays log output from services
docker-compose -f docker-compose.local.yml logs
```
