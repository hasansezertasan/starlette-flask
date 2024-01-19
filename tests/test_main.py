import pytest
from a2wsgi import WSGIMiddleware
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from flask import Flask, jsonify, session

from starlette_flask.middleware.sessions import SessionMiddleware

secret_key = "super-secret"

# Flask Application
flask_app = Flask(__name__)
flask_app.config["SECRET_KEY"] = secret_key

# FastAPI Application
fastapi_application = FastAPI()
fastapi_application.add_middleware(SessionMiddleware, secret_key="super-secret")


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


@fastapi_application.get("/set-session")
async def starlette_set_session(request: Request):
    request.session.update({"application": "fastapi"})
    return {"message": "Session set"}


@fastapi_application.get("/get-session")
async def starlette_get_session(request: Request):
    return {"message": request.session.get("application", None)}


@fastapi_application.get("/delete-session")
async def starlette_delete_session(request: Request):
    request.session.pop("application")
    return {"message": "Session deleted"}


# Main FastAPI Application
app = FastAPI()
# Mount Sub Applications
app.mount("/flask-application", WSGIMiddleware(flask_app))
app.mount("/fastapi-application", fastapi_application)


client = TestClient(app)


@pytest.mark.parametrize(
    "left, right",
    [
        ("flask", "fastapi"),
        ("fastapi", "flask"),
    ],
)
def test_session(left: str, right: str):
    # Zero
    response = client.get(f"/{left}-application/get-session")
    assert response.status_code == 200
    assert response.json() == {"message": None}

    response = client.get(f"/{right}-application/get-session")
    assert response.status_code == 200
    assert response.json() == {"message": None}

    response = client.get(f"/{left}-application/set-session")
    assert response.status_code == 200

    response = client.get(f"/{left}-application/get-session")
    assert response.status_code == 200
    assert response.json() == {"message": left}

    response = client.get(f"/{right}-application/get-session")
    assert response.status_code == 200
    assert response.json() == {"message": left}

    response = client.get(f"/{left}-application/delete-session")
    assert response.status_code == 200

    response = client.get(f"/{left}-application/get-session")
    assert response.status_code == 200
    assert response.json() == {"message": None}

    response = client.get(f"/{right}-application/get-session")
    assert response.status_code == 200
    assert response.json() == {"message": None}
