from datetime import date, datetime

from flask.cli import FlaskGroup
from sqlalchemy.exc import OperationalError

from src import create_app
from src.database import db, Bucket, Item


cli = FlaskGroup(create_app=create_app)


@cli.command("create_db")
def create_db():
    _create_db()


@cli.command("seed_prod_db")
def seed_prod_db():
    _seed_required_data()


@cli.command("seed_test_db")
def seed_test_db():
    _seed_required_data()
    _seed_test_data()


def _create_db():
    try:
        db.drop_all()
    except OperationalError:
        pass  # Likely means database does not exist
    db.create_all()
    db.session.commit()


def _seed_required_data():
    if db.session.query(Bucket).filter_by(title="Inbox").count() == 0:
        inbox = Bucket(
            title="Inbox",
            description="Collection of items without a bucket",
            can_deactivate=False,
        )
        db.session.add(inbox)
        db.session.commit()


def _seed_test_data():
    bucket = Bucket(
        title="My stuff development",
        description="Software development tracking for this system",
    )
    bucket.items.append(Item(title="Bucket page", completed_time=datetime(2020, 7, 28, 8, 4)))
    bucket.items.append(Item(title="Deactivate bucket"))
    bucket.items.append(Item(title="Refactor models and views"))
    bucket.items.append(Item(title="Home page due, next and flagged"))
    bucket.items.append(Item(title="Move item to different bucket"))
    bucket.items.append(Item(title="Item ordering"))
    bucket.items.append(Item(title="Change item ordering"))
    bucket.items.append(
        Item(
            title="Fix production deployment",
            description="Reverse proxy loses port information during redirects.",
            flagged=True,
        )
    )
    bucket.items.append(Item(title="Timezone handling"))
    bucket.items.append(Item(title="Production deployment"))
    bucket.items.append(Item(title="Data backup"))
    bucket.items.append(Item(title="Acceptance tests", due_date=date(2020, 7, 31)))
    bucket.items.append(Item(title="Version 1.0", due_date=date(2020, 8, 8)))
    db.session.add(bucket)
    db.session.commit()


if __name__ == "__main__":
    cli()
