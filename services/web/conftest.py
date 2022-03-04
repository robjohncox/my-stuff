import pytest
from src import create_app
from src.database import db


@pytest.fixture
def test_client():
    flask_app = create_app()
    # Ideally, we would not disable this for unit tests, but it does make them cleaner
    flask_app.config["WTF_CSRF_ENABLED"] = False
    testing_client = flask_app.test_client()
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
    # Create the database and the database tables
    db.create_all()
    # Return the test client and run the test
    yield testing_client
    # Drop database tables after the test
    db.drop_all()
    # Clean up the app context after the test
    ctx.pop()
