# preprocessing-api

## Stacks

- Main programming language: `Python3`
- Framework: [Sanic](https://github.com/channelcat/sanic)
- Configuration: [Python Dotenv](https://github.com/theskumar/python-dotenv)

Dependencies:

- Sanic (of course)
- Python dotenv: Manage environment variable for configurations
- aiohttp: Async http client/server library (actually you should got this lib from sanic itself, i just need to make sure about it)
- Fabric3: Manage automated tasks

---

## Getting Started

To run the project, just run

```
docker-compose up
```




Install dependencies :

```
pip install -r requirements.txt
```

Start sanic:

```
python main.py
```

Start with debug:

```
python main.py --debug
```

Enable access logs:

```
python main.py --access
```

Read more about command line options:

```
python main.py -h
```

---

## Structures

`apps` 

Put all of your apps here.  I'm just following Django modular apps here.

`core`

This place used to put all core library (not business logic) like for helpers
and also for sanic's extensions like custom exception handler or custom middlewares.

`main`

You need to install all of your apps or extentions by registering their `blueprint`,
for more detail, you can see the code inside `main.py`.

---

## Settings

We are using `python-dotenv` to manage all of your configurations.  There is file named
with `env.default` , put all of your config keys here (do not put your sensitive values, like
your api key).  You need to copy and rename the file to `.env` (this file listed at `.gitignore`),
and configure your configuration key and values in this file (`.env`).

You need to add all of those configurations to `settings.py`, then all your configurations will
be loaded inside sanic's lifecycle, you can access these configurations from your blueprint's apps, using
`request.app.config`.

---

## Automate Tests & Tasks

For all tests it will separated by their modules, examples:

- tests/apps
- tests/core

It will help you to select your context when running test. 

Besides of automated tests, this repo also provide basic automated tasks using [Fabric3](https://github.com/mathiasertl/fabric/).

You can setup your tasks in `fabfile.py`.  An example to run your tests:

```
fab test:apps
```

---