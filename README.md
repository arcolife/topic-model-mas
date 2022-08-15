- [Topic-modelling AEA](#topic-modelling-aea)
  - [Introduction](#introduction)
  - [Creating an Agent](#creating-an-agent)
    - [Setup](#setup)
  - [Add a skill](#add-a-skill)
  - [External data-source](#external-data-source)
  - [Testing](#testing)
  - [Frontend](#frontend)

# Topic-modelling AEA

## Introduction

This is a topic-modelling AEA that collects textual data from third party (external) data-source and lets the agents publish the agreed-upon top 3 topics from daily updates into a shared note-taking space.

Refs:
- [AEA Quickstart doc](docs/aea-quickstart.md).

## Creating an Agent

Overview docs:
- https://docs.autonolas.network/quick_start/
- https://www.autonolas.network/academy/education-track

### Setup

refs: 
- https://open-aea.docs.autonolas.tech/development-setup/
- https://github.com/fetchai/agents-template


Install pre-requisites:

```sh
touch Pipfile && pipenv --python 3.10
pipenv install open-autonomy
pipenv shell
```

Initialize new agent
```sh
autonomy init --remote
cd packages
aea create topic_aggregator
aea search --local skills
# Searching for ""...
# No skills found.
```

## Add a skill

```sh
aea scaffold skill topic_extractor

```

## External data-source

refs:
- https://github.com/valory-xyz/open-aea/tree/main/packages/fetchai/connections/http_client

## Testing

refs:
- https://open-aea.docs.autonolas.tech/quickstart/#test-quickstart
- https://github.com/valory-xyz/open-autonomy/blob/main/tests/test_agents/test_hello_world.py

```sh
pipenv run pytest test.py
```

## Frontend

You could drump up a frontend via [React](https://reactjs.org/).

refs:
- https://github.com/valory-xyz/ethlisbon/tree/master/frontend

