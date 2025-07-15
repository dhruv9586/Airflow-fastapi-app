import json
from base64 import b64decode
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from jwt import decode, get_unverified_header
from pydantic import TypeAdapter

from tests.utils.common import random_string
from tronapi.core.config import Configuration
from tronapi.endpoints.users import UserTokenResponse
from tronapi.security.authentication.handlers.models import User
from tronapi.settings import get_settings

# client headers is case insensitive dictionary, so simulating multiple same headers by
# using capitalization (slightly hacky...) test_headers = [(input, expected_output)]
# TODO(Nick): currently not testing authorization, only authentication

API_VERSION = "experimental"
CURRENT_USER_BASE_PATH = f"/{API_VERSION}/current_user"

settings = get_settings()

path = f"{settings.url_version}/current_user"
UUID_ID = str(uuid4())
favorites_path = f"{settings.url_version}/current_user/favorites"
current_user_parameters = [
    ({}, 200, {"uuid": None, "email": None, "firstname": None, "lastname": None}),
    (
        {"email": "pytest@pytest.test"},
        200,
        {
            "uuid": None,
            "email": "pytest@pytest.test",
            "firstname": None,
            "lastname": None,
        },
    ),
    (
        {"firstname": "pytest", "lastname": "User"},
        200,
        {"uuid": None, "email": None, "firstname": "pytest", "lastname": "User"},
    ),
    (
        {"uuid": UUID_ID},
        200,
        {"uuid": UUID_ID, "email": None, "firstname": None, "lastname": None},
    ),
    (
        {
            "uuid": UUID_ID,
            "email": "pytest@pytest.test",
            "firstname": "pytest",
            "lastname": "User",
        },
        200,
        {
            "uuid": UUID_ID,
            "email": "pytest@pytest.test",
            "firstname": "pytest",
            "lastname": "User",
        },
    ),
    ({"uuid": "bad"}, 401, {"detail": "User lacks valid authentication credentials."}),
]

validuser = User(
    uuid=UUID("dbea6c59-0b5f-49b8-a365-576c8fdb7a5e"),
    email="valid_email@test.local",
    firstname="valid_firstname",
    lastname="valid_lastname",
)
validuser2 = User(
    uuid=UUID("eb3115ad-6a83-4efe-b115-d3ec9fe339c5"),
    email="valid_email2@test.local",
    firstname="valid_firstname2",
    lastname="valid_lastname2",
)
# Serialize and load forces all values to be decomposed to simple types
validuser_dict = json.loads(validuser.json())
validuser2_dict = json.loads(validuser2.json())


@pytest.mark.parametrize(
    ("headers", "expected_status", "expected_response"), current_user_parameters
)
def test_current_user(
    headers: dict, expected_status: int, expected_response: dict, client: TestClient
) -> None:
    """Test how various combinations of headers are returned."""
    # Test criteria:
    # * No headers -> All None
    # * X headers -> X set, rest None
    # * Multiple of the same header -> Last provided
    # * UUID validated if supplied.

    response = client.get(path, headers=headers)
    assert response.status_code == expected_status
    assert response.json() == expected_response


check_auth_parameters = [
    ({}, 401, {"detail": "User lacks valid authentication credentials."}),
    (
        {"email": "pytest@pytest.test"},
        401,
        {"detail": "User lacks valid authentication credentials."},
    ),
    (
        {"firstname": "pytest", "lastname": "User"},
        401,
        {"detail": "User lacks valid authentication credentials."},
    ),
    (
        {"uuid": UUID_ID},
        200,
        {
            "uuid": UUID_ID,
            "email": None,
            "firstname": None,
            "lastname": None,
        },
    ),
    (
        {
            "uuid": UUID_ID,
            "email": "pytest@pytest.test",
            "firstname": "pytest",
            "lastname": "User",
        },
        200,
        {
            "uuid": UUID_ID,
            "email": "pytest@pytest.test",
            "firstname": "pytest",
            "lastname": "User",
        },
    ),
    (
        {
            "uuid": "bad",
            "email": "pytest@pytest.test",
            "firstname": "pytest",
            "lastname": "User",
        },
        401,
        {"detail": "User lacks valid authentication credentials."},
    ),
]


@pytest.mark.parametrize(
    ("headers", "expected_status", "expected_response"), check_auth_parameters
)
def test_check_auth(
    headers: dict, expected_status: int, expected_response: dict, client: TestClient
) -> None:
    """Test how various combinations of headers are accepted as valid."""
    # Test criteria:
    # * No headers -> Unauthenticated
    # * Some headers -> Unauthenticated
    # * All headers -> Authenticated
    # * UUID validated if supplied.
    response = client.get(f"{path}/is_authenticated", headers=headers)
    assert response.status_code == expected_status
    assert response.json() == expected_response


def test_end_session(client: TestClient) -> None:
    """Test deleting the token cookie."""
    response = client.delete(f"{path}/session")
    assert response.status_code == 204
    set_cookie_header: str = response.headers.get("set-cookie")
    assert set_cookie_header.startswith('token=""')


def test_update_user_favorites(
    authorized_client: TestClient,
    user: User,  # pylint: disable=unused-argument
) -> None:
    """Test the updating user favorites workflow."""
    # Post invalid config needed by Airflow to endpoint
    # this call should produce a 422, even though the call to recognizer would have been successful
    response = authorized_client.post(
        favorites_path,
        json={"favorites": "test_worflow", "is_delete": False},
    )
    assert response.status_code == 200
    assert "User favorites updated successfull" in response.json()["message"]


# region Test Create Own API Token


def test_create_own_api_token(
    authorized_client: TestClient, user: User, configuration: Configuration
) -> None:
    """Tests whether an API token for themselves can be created by an authorized user."""
    assert configuration.API_TOKEN_SIGNING_KEY is not None
    assert isinstance(user.email, str)

    comment = "pytest token"
    expires_in = timedelta(days=365)

    response = authorized_client.post(
        f"{CURRENT_USER_BASE_PATH}/api_tokens",
        json={"comment": comment, "expires_in": expires_in.total_seconds()},
    )
    assert response.status_code == 201
    ta = TypeAdapter(UserTokenResponse)
    token_response = ta.validate_python(response.json())

    # Decode the token and check validity
    headers = get_unverified_header(token_response.token)
    token = decode(
        token_response.token,
        key=b64decode(configuration.API_TOKEN_SIGNING_KEY.get_secret_value()),
        algorithms=["HS256"],
        audience=configuration.API_TOKEN_AUDIENCE,
    )

    # Check headers
    assert headers["alg"] == "HS256"
    assert headers["kid"] == configuration.API_TOKEN_KEY_ID
    assert headers["typ"] == "JWT"

    # Check reserved claims
    assert UUID(token["jti"])
    assert token["iss"] == configuration.API_TOKEN_AUDIENCE
    assert UUID(token["sub"]) == user.uuid
    assert token["iat"] == token["nbf"]
    assert token["exp"] - token["iat"] == expires_in.total_seconds()
    assert token["exp"] == int(token_response.expires_at.timestamp())

    # Check custom claims
    assert UUID(token["custom-uuid"]) == user.uuid
    assert token["custom-email"] == user.email
    assert token["custom-firstname"] == user.firstname
    assert token["custom-lastname"] == user.lastname
    assert token["custom-comment"] == comment


async def test_error_create_own_api_token_long_comment(
    authorized_client: TestClient, user: User, configuration: Configuration
) -> None:
    """Tests error on creating an API token with a comment that's too long."""
    assert configuration.API_TOKEN_SIGNING_KEY is not None
    assert isinstance(user.email, str)

    comment = "A" * 1000
    expires_in = timedelta(days=365)

    response = authorized_client.post(
        f"{CURRENT_USER_BASE_PATH}/api_tokens",
        json={"comment": comment, "expires_in": expires_in.total_seconds()},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "comment String should have at most 256 characters"
    }


def test_error_create_own_api_token_bad_expiry(
    authorized_client: TestClient, user: User, configuration: Configuration
) -> None:
    """Tests error on creating an API token with an invalid expiration time."""
    assert configuration.API_TOKEN_SIGNING_KEY is not None
    assert isinstance(user.email, str)

    comment = "pytest token"
    bad_expires_in = random_string()

    response = authorized_client.post(
        f"{CURRENT_USER_BASE_PATH}/api_tokens",
        json={"comment": comment, "expires_in": bad_expires_in},
    )
    assert response.status_code == 422
    resp = response.json()
    assert resp["detail"].startswith("expires_in Input should be a valid timedelta")


def test_error_create_own_api_token_unauthorized(
    unauthorized_client: TestClient,
    unauthorized_user: User,
    configuration: Configuration,
) -> None:
    """Tests error on creating an API token by an unauthorized user."""
    assert configuration.API_TOKEN_SIGNING_KEY is not None
    assert isinstance(unauthorized_user.email, str)

    comment = "pytest token"
    expires_in = timedelta(days=365)

    response = unauthorized_client.post(
        f"{CURRENT_USER_BASE_PATH}/api_tokens",
        json={"comment": comment, "expires_in": expires_in.total_seconds()},
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "User is not authorized to perform this action on this resource.",
        "user": {
            "email": unauthorized_user.email,
            "firstname": unauthorized_user.firstname,
            "lastname": unauthorized_user.lastname,
            "uuid": str(unauthorized_user.uuid),
        },
    }


# endregion Create User API Token
