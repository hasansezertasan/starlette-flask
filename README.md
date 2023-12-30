# starlette-flask

[![PyPI - Version](https://img.shields.io/pypi/v/starlette-flask.svg)](https://pypi.org/project/starlette-flask)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/starlette-flask.svg)](https://pypi.org/project/starlette-flask)

-----

Session Middleware for Starlette/FastAPI Applications based on Flask Session Decoding and Encoding.

**Table of Contents**

- [starlette-flask](#starlette-flask)
  - [Installation](#installation)
  - [Story](#story)
  - [Real World Example](#real-world-example)
  - [License](#license)

## Installation

```console
pip install starlette-flask
```

## Story

I was migrating from [Flask] to [FastAPI] and I found out that I could use my existing [Flask] applications with [FastAPI] (thanks to [a2wsgi]) application.

> I must tell you this: Many of my [Flask] applications depend on third-party [Flask] extensions like [Flask Admin], [Flask Login], and [Flask-JWT-Extended]

So I searched how to couple [Flask] and [FastAPI] and [found a way](https://fastapi.tiangolo.com/advanced/wsgi/#using-wsgimiddleware). But there was a problem... I wasn't able to access the session data between [Flask] and [FastAPI] applications. I mean I was able to CRUD session data on the [Flask] side and [FastAPI] side but I couldn't CRUD the session data inside [FastAPI] that was CRUDed by [Flask], so I started this [discussion](https://github.com/tiangolo/fastapi/discussions/9318) in the [FastAPI] repository. Back then I wasn't able to solve this, so I decided not to use [Flask Login] and [Flask Admin] anymore...

But you can see that the discussion didn't get any answers from March to September. It was bothering me, so I decided to solve it myself. I took a look at the source code of [Flask] and [Starlette] (backend core of [FastAPI]). I found that they used different methods to sign the session data and [Starlette] kept re-signing the session data even if it wasn't created, updated, deleted, or even read, that was the problem... I needed a custom `SessionMiddleware` that uses the same method as [Flask] to sign the session data and I did implement it.

Here are some related discussions/issues/pull requests:

- [Sharing Session Data between Mounted Applications · tiangolo/fastapi · Discussion #9318](https://github.com/tiangolo/fastapi/discussions/9318)
- [Use Base64Url encoding and decoding in Session Cookie by allezxandre · Pull Request #1922 · encode/starlette](https://github.com/encode/starlette/pull/1922)
- [SessionMiddleware sends a new set-cookie for every request, with unintended results · Issue #2019 · encode/starlette](https://github.com/encode/starlette/issues/2019)
- [Create More Flexable SessionMiddleware · encode/starlette · Discussion #2256](https://github.com/encode/starlette/discussions/2256)
- [SessionMiddleware may create malformed cookie · Issue #1259 · encode/starlette](https://github.com/encode/starlette/issues/1259)
- [Added `allow_path_regex` to the `SessionMiddleware` by hasansezertasan · Pull Request #2316 · encode/starlette](https://github.com/encode/starlette/pull/2316)

Check out [Middleware - Starlette](https://www.starlette.io/middleware/) page to learn more about middlewares in [Starlette].

## Real World Example

So what's the problem? Let's say you have a [Flask] application and it was live for a long time. You want to migrate to [FastAPI] but you don't want your users to lose their session data. And to be honest, migrating is not an easy process. You might want to take it slow and get the benefit of FastAPI features like mounting an application to another application.

Let's try to mount a [Flask] application to a [FastAPI] application.

```python
from fastapi import FastAPI, Request, Response
from flask import Flask, jsonify, session, request
from starlette.middleware.sessions import SessionMiddleware
from a2wsgi import WSGIMiddleware

secret_key = "super-secret"


flask_app = Flask(__name__)
flask_app.config["SECRET_KEY"] = secret_key


@flask_app.get("/")
def flask_index():
    return jsonify({"message": "Hello World from Flask Application"})


@flask_app.get("/set-session")
def flask_set_session():
    session["application"] = "flask"
    session.modified = True
    return jsonify({"message": "Session set"})


@flask_app.get("/get-session")
def flask_get_session():
    return jsonify({"message": session.get("application", None)})


@flask_app.get("/delete-session")
def flask_delete_session():
    session.pop("application")
    session.modified = True
    return jsonify({"message": "Session deleted"})


@flask_app.before_request
def before_request():
    print(session.items())

@flask_app.after_request
def after_request(response):
    print(session.items())
    return response


fastapi_application = FastAPI()
fastapi_application.add_middleware(
    SessionMiddleware,
    secret_key="super-secret",
)


@fastapi_application.middleware("http")
async def starlette_add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Process-Time"] = "100"
    print(response.headers)
    return response


@fastapi_application.get("/")
async def starlette_index(req: Request):
    return {"message": "Hello World from FastAPI Application"}


@fastapi_application.get("/set-session")
async def starlette_set_session(req: Request):
    req.session.update({"application": "fastapi"})
    return {"message": "Session set"}


@fastapi_application.get("/get-session")
async def starlette_get_session(req: Request):
    return {"message": req.session.get("application", None)}


@fastapi_application.get("/delete-session")
async def starlette_delete_session(req: Request):
    req.session.pop("application")
    return {"message": "Session deleted"}


app = FastAPI()
app.mount("/flask-application", WSGIMiddleware(flask_app))
app.mount("/fastapi-application", fastapi_application)

```

The problem here is this: If you set a session in [Flask] application, you can't get it from [FastAPI] application, and vice versa. At the same time, beyond accessing the session data, these two applications overwrite each other's session data. That's because they use different methods to sign the session data.

Since they use different methods to sign the session data, they can't decode each other's session data. What can we do? We can use `starlette-flask` to solve this problem.

All you need to do is this:

```diff
- from starlette.middleware.sessions import SessionMiddleware
+ from starlette_flask.middleware.sessions import SessionMiddleware
```

## License

`starlette-flask` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

[FastAPI]: https://github.com/tiangolo/fastapi
[Starlette]: https://github.com/encode/starlette
[Flask]: https://github.com/pallets/flask
[Flask Admin]: https://github.com/flask-admin/flask-admin
[Flask Login]: https://github.com/maxcountryman/flask-login
[a2wsgi]: https://github.com/abersheeran/a2wsgi
[Flask-JWT-Extended]: https://github.com/vimalloc/flask-jwt-extended
