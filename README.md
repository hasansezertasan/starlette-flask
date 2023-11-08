# starlette-flask

[![PyPI - Version](https://img.shields.io/pypi/v/starlette-flask.svg)](https://pypi.org/project/starlette-flask)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/starlette-flask.svg)](https://pypi.org/project/starlette-flask)

-----

**Table of Contents**

- [starlette-flask](#starlette-flask)
  - [Installation](#installation)
  - [Story](#story)
  - [License](#license)

## Installation

```console
pip install starlette-flask
```

## Story

I was migrating from [Flask] to [FastAPI] and I found out that I could mount a [Flask] application to a [FastAPI] (thanks to [Starlette]) application. I had an admin panel in my [Flask] application based on [Flask Admin] and I had an authentication system using [Flask Login].

So I mounted the thing...

There was a problem: I wasn't able to share and CRUD the session data between [Flask] Application and [FastAPI] application, so i started this [discussion](https://github.com/tiangolo/fastapi/discussions/9318) in the [FastAPI] repository. Back then I wasn't able to solve this problem, so I decided not to use [Flask] Login and [Flask] Admin anymore.

But you can see that the discussion didn't get any answers from march to september. It bothered me, so I decided to solve it myself. I took a look at the source code of [Flask] and [Starlette]. They used different methods to sign the session data, that was the problem... I decided to implement a custom `SessionMiddleware` that uses the same method as [Flask] to sign the session data. And it worked!

Here are some related discussions/issues/pull requests:

- [Sharing Session Data between Mounted Applications · tiangolo/fastapi · Discussion #9318](https://github.com/tiangolo/fastapi/discussions/9318)
- [Use Base64Url encoding and decoding in Session Cookie by allezxandre · Pull Request #1922 · encode/starlette](https://github.com/encode/starlette/pull/1922)
- [SessionMiddleware sends a new set-cookie for every request, with unintended results · Issue #2019 · encode/starlette](https://github.com/encode/starlette/issues/2019)
- [Create More Flexable SessionMiddleware · encode/starlette · Discussion #2256](https://github.com/encode/starlette/discussions/2256)
- [SessionMiddleware may create malformed cookie · Issue #1259 · encode/starlette](https://github.com/encode/starlette/issues/1259)

Check out [Middleware - Starlette](https://www.starlette.io/middleware/) page to learn more about middlewares in [Starlette].

## License

`starlette-flask` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

[FastAPI]: https://github.com/tiangolo/fastapi
[Starlette]: https://github.com/encode/starlette
[Flask]: https://github.com/pallets/flask
[Flask Admin]: https://github.com/flask-admin/flask-admin
[Flask Login]: https://github.com/maxcountryman/flask-login
