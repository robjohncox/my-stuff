from datetime import date

from unittest.mock import patch

from src.database import db, Bucket, Item


class TestHomePage:
    def test_redirects_to_inbox_bucket_page(self, test_client):
        _create_inbox_bucket()
        _create_bucket(title="Shopping", description="Groceries we need")

        response = test_client.get("/", follow_redirects=True)

        assert response.status_code == 200
        assert b"Inbox" in response.data
        assert b"Shopping" in response.data
        assert b"<h2>Inbox</h2>" in response.data
        assert b"<p>Random things</p>" in response.data

    def test_no_inbox__404_error(self, test_client):
        response = test_client.get("/")

        assert response.status_code == 404


class TestBucketPage:
    def test_bucket_page(self, test_client):
        _create_inbox_bucket()
        bucket = _create_bucket(
            title="Shopping",
            description="Groceries we need",
            item_titles=["Tomatoes", "Carrots"],
        )

        response = test_client.get(f"/bucket/{bucket.id}/")

        assert response.status_code == 200
        assert b"Inbox" in response.data
        assert b"Shopping" in response.data
        assert b"<h2>Shopping</h2>" in response.data
        assert b"<p>Groceries we need</p>" in response.data
        assert b"<td>Tomatoes</td>" in response.data
        assert b"<td>Carrots</td>" in response.data

    def test_bucket_not_found__404_error(self, test_client):
        unknown_bucket_id = 9

        response = test_client.get(f"/bucket/{unknown_bucket_id}/")

        assert response.status_code == 404

    def test_quick_create_item(self, test_client):
        bucket = _create_bucket(
            title="Shopping",
            description="Groceries we need",
            item_titles=["Tomatoes"],
        )

        response = test_client.post(f"/bucket/{bucket.id}/", data={"title": "Zucchini"})

        assert response.status_code == 200
        assert b"<td>Zucchini</td>" in response.data
        item = _get_item("Zucchini")
        assert item.bucket == bucket
        assert item.description is None
        assert item.created_time is not None
        assert item.due_date is None
        assert item.completed_time is None
        assert not item.flagged

    def test_title_not_provided__validation_error(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(f"/bucket/{bucket.id}/", data={"title": ""})

        assert response.status_code == 200
        assert b"Enter a title." in response.data

    def test_title_too_long__validation_error(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(f"/bucket/{bucket.id}/", data={"title": "a" * 129})

        assert response.status_code == 200
        assert b"No longer than 128 characters." in response.data


class TestCreateBucket:
    def test_create_bucket__get(self, test_client):
        response = test_client.get("/bucket/create/")

        assert response.status_code == 200

    def test_create_bucket__post(self, test_client):
        _create_inbox_bucket()

        response = test_client.post(
            "/bucket/create/",
            data={"title": "Shopping", "description": "List of groceries"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"<h2>Shopping</h2>" in response.data
        bucket = _get_bucket("Shopping")
        assert bucket.title == "Shopping"
        assert bucket.description == "List of groceries"
        assert bucket.can_deactivate
        assert bucket.deactivated_time is None

    def test_title_not_provided__validation_error(self, test_client):
        response = test_client.post(
            "/bucket/create/",
            data={"title": "", "description": "List of groceries"},
        )

        assert response.status_code == 200
        assert b"Enter a title." in response.data

    def test_title_too_long__validation_error(self, test_client):
        response = test_client.post(
            "/bucket/create/",
            data={"title": "a" * 33, "description": "List of groceries"},
        )

        assert response.status_code == 200
        assert b"No longer than 32 characters." in response.data

    def test_title_already_exists__validation_error(self, test_client):
        _create_bucket(title="Shopping")

        response = test_client.post(
            "/bucket/create/",
            data={"title": "Shopping", "description": "List of groceries"},
        )

        assert response.status_code == 200
        assert b"Bucket title must be unique." in response.data

    def test_description_not_provided__validation_error(self, test_client):
        response = test_client.post(
            "/bucket/create/",
            data={"title": "Shopping", "description": ""},
        )

        assert response.status_code == 200
        assert b"Enter a description." in response.data


class TestUpdateBucket:
    def test_update_bucket__get(self, test_client):
        bucket = _create_bucket(title="Shopping")

        response = test_client.get(f"/bucket/{bucket.id}/update/")

        assert response.status_code == 200

    def test_update_bucket__post(self, test_client):
        bucket = _create_bucket(title="Shopping", description="List of groceries")

        response = test_client.post(
            f"/bucket/{bucket.id}/update/",
            data={"title": "Stuff to buy", "description": "I like shopping"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"<h2>Stuff to buy</h2>" in response.data
        bucket = _get_bucket("Stuff to buy")
        assert bucket.title == "Stuff to buy"
        assert bucket.description == "I like shopping"
        assert bucket.can_deactivate
        assert bucket.deactivated_time is None

    def test_update_where_data_does_not_change(self, test_client):
        bucket = _create_bucket(title="Shopping", description="List of groceries")

        response = test_client.post(
            f"/bucket/{bucket.id}/update/",
            data={"title": "Shopping", "description": "List of groceries"},
            follow_redirects=True,
        )

        print(response.data)
        assert response.status_code == 200
        assert b"<h2>Shopping</h2>" in response.data
        bucket = _get_bucket("Shopping")
        assert bucket.title == "Shopping"
        assert bucket.description == "List of groceries"

    def test_title_not_provided__validation_error(self, test_client):
        bucket = _create_bucket(title="Shopping")

        response = test_client.post(
            f"/bucket/{bucket.id}/update/",
            data={"title": "", "description": "List of groceries"},
        )

        assert response.status_code == 200
        assert b"Enter a title." in response.data

    def test_title_too_long__validation_error(self, test_client):
        bucket = _create_bucket(title="Shopping")

        response = test_client.post(
            f"/bucket/{bucket.id}/update/",
            data={"title": "a" * 33, "description": "List of groceries"},
        )

        assert response.status_code == 200
        assert b"No longer than 32 characters." in response.data

    def test_title_already_exists__validation_error(self, test_client):
        _create_bucket(title="Stuff to buy")
        bucket = _create_bucket(title="Shopping")

        response = test_client.post(
            f"/bucket/{bucket.id}/update/",
            data={"title": "Stuff to buy", "description": "List of groceries"},
        )

        assert response.status_code == 200
        assert b"Bucket title must be unique." in response.data

    def test_description_not_provided__validation_error(self, test_client):
        bucket = _create_bucket(title="Shopping")

        response = test_client.post(
            f"/bucket/{bucket.id}/update/",
            data={"title": "Shopping", "description": ""},
        )

        assert response.status_code == 200
        assert b"Enter a description." in response.data


class TestCreateItem:
    def test_create_item__get(self, test_client):
        bucket = _create_bucket()

        response = test_client.get(f"/bucket/{bucket.id}/item/create/")

        assert response.status_code == 200

    def test_create_item__post(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(
            f"/bucket/{bucket.id}/item/create/",
            data={
                "title": "Zucchini",
                "description": "Vegetable also known as a courgette",
                "due_date": "2020-01-30",
                "flagged": True,
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Zucchini" in response.data
        item = _get_item("Zucchini")
        assert item.bucket == bucket
        assert item.description == "Vegetable also known as a courgette"
        assert item.created_time is not None
        assert item.due_date == date(2020, 1, 30)
        assert item.completed_time is None
        assert item.flagged

    def test_only_supplying_required_fields(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(
            f"/bucket/{bucket.id}/item/create/",
            data={"title": "Zucchini"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"<td>Zucchini</td>" in response.data
        item = _get_item("Zucchini")
        assert item.bucket == bucket
        assert item.description is None
        assert item.created_time is not None
        assert item.due_date is None
        assert item.completed_time is None
        assert not item.flagged

    def test_bucket_not_found__404_error(self, test_client):
        bucket_id = 9

        response = test_client.post(
            f"/bucket/{bucket_id}/item/create/",
            data={"title": "Zucchini"},
            follow_redirects=True,
        )

        assert response.status_code == 404

    def test_title_not_provided__validation_error(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(f"/bucket/{bucket.id}/item/create/", data={"title": ""})

        assert response.status_code == 200
        assert b"Enter a title." in response.data

    def test_title_too_long__validation_error(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(f"/bucket/{bucket.id}/item/create/", data={"title": "a" * 129})

        assert response.status_code == 200
        assert b"No longer than 128 characters." in response.data

    def test_due_date_invalid_format__validation_error(self, test_client):
        bucket = _create_bucket()

        response = test_client.post(
            f"/bucket/{bucket.id}/item/create/",
            data={"title": "Zucchini", "due_date": "20200130"},
        )

        assert response.status_code == 200
        assert b"Not a valid date value" in response.data


class TestUpdateItem:
    def test_update_item__get(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)

        response = test_client.get(f"/bucket/{bucket.id}/item/{item.id}/update/")

        assert response.status_code == 200

    def test_update_item__post(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket, "Tomatoes")

        response = test_client.post(
            f"/bucket/{bucket.id}/item/{item.id}/update/",
            data={
                "title": "Zucchini",
                "description": "Vegetable also known as a courgette",
                "due_date": "2020-01-30",
                "flagged": True,
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Zucchini" in response.data
        updated_item = _get_item("Zucchini")
        assert updated_item.id == item.id
        assert updated_item.bucket == bucket
        assert updated_item.description == "Vegetable also known as a courgette"
        assert updated_item.created_time is not None
        assert updated_item.due_date == date(2020, 1, 30)
        assert updated_item.completed_time is None
        assert updated_item.flagged

    def test_bucket_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)
        bucket_id = 9

        response = test_client.post(
            f"/bucket/{bucket_id}/item/{item.id}/update/",
            data={"title": "Zucchini"},
            follow_redirects=True,
        )

        assert response.status_code == 404

    def test_item_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item_id = 9

        response = test_client.post(
            f"/bucket/{bucket.id}/item/{item_id}/update/",
            data={"title": "Zucchini"},
            follow_redirects=True,
        )

        assert response.status_code == 404

    def test_title_not_provided__validation_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)

        response = test_client.post(
            f"/bucket/{bucket.id}/item/{item.id}/update/", data={"title": ""}
        )

        assert response.status_code == 200
        assert b"Enter a title." in response.data

    def test_title_too_long__validation_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)

        response = test_client.post(
            f"/bucket/{bucket.id}/item/{item.id}/update/", data={"title": "a" * 129}
        )

        assert response.status_code == 200
        assert b"No longer than 128 characters." in response.data

    def test_due_date_invalid_format__validation_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)

        response = test_client.post(
            f"/bucket/{bucket.id}/item/{item.id}/update/",
            data={"title": "Zucchini", "due_date": "20200130"},
        )

        assert response.status_code == 200
        assert b"Not a valid date value" in response.data


class TestCompleteItem:
    def test_complete_item(self, test_client):
        bucket = _create_bucket()
        tomatoes = _create_item(bucket, "Tomatoes")
        _create_item(bucket, "Carrots")

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{tomatoes.id}/complete/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"<td>Tomatoes</td>" not in response.data
        assert b"<td>Carrots</td>" in response.data
        item = _get_item("Tomatoes")
        assert item.completed_time is not None

    def test_item_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item_id = 9

        response = test_client.get(f"/bucket/{bucket.id}/item/{item_id}/complete/")

        assert response.status_code == 404

    def test_bucket_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)
        bucket_id = 9

        response = test_client.get(f"/bucket/{bucket_id}/item/{item.id}/complete/")

        assert response.status_code == 404


class TestItemDueDatePlusOneDay:
    def test_item_due_date_plus_one_day(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket, "New house", due_date=date(2020, 1, 1))

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{item.id}/due_date_plus_one_day/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        item = _get_item("New house")
        assert item.due_date == date(2020, 1, 2)

    @patch("src.views.date")
    def test_no_due_date_set__due_date_is_tomorrow(self, mock_date_lib, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket, "New house", due_date=None)
        mock_date_lib.today.return_value = date(2020, 1, 1)

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{item.id}/due_date_plus_one_day/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        item = _get_item("New house")
        assert item.due_date == date(2020, 1, 2)

    def test_item_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item_id = 9

        response = test_client.get(f"/bucket/{bucket.id}/item/{item_id}/due_date_plus_one_day/")

        assert response.status_code == 404

    def test_bucket_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)
        bucket_id = 9

        response = test_client.get(f"/bucket/{bucket_id}/item/{item.id}/due_date_plus_one_day/")

        assert response.status_code == 404


class TestFlagItem:
    def test_flag_item(self, test_client):
        bucket = _create_bucket()
        tomatoes = _create_item(bucket, "Tomatoes")

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{tomatoes.id}/flag/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        item = _get_item("Tomatoes")
        assert item.flagged

    def test_item_already_flagged__remains_flagged(self, test_client):
        bucket = _create_bucket()
        tomatoes = _create_item(bucket, "Tomatoes", flagged=True)

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{tomatoes.id}/flag/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        item = _get_item("Tomatoes")
        assert item.flagged

    def test_item_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item_id = 9

        response = test_client.get(f"/bucket/{bucket.id}/item/{item_id}/flag/")

        assert response.status_code == 404

    def test_bucket_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)
        bucket_id = 9

        response = test_client.get(f"/bucket/{bucket_id}/item/{item.id}/flag/")

        assert response.status_code == 404


class TestUnflagItem:
    def test_unflag_item(self, test_client):
        bucket = _create_bucket()
        tomatoes = _create_item(bucket, "Tomatoes", flagged=True)

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{tomatoes.id}/unflag/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        item = _get_item("Tomatoes")
        assert not item.flagged

    def test_item_not_flagged__remains_unflagged(self, test_client):
        bucket = _create_bucket()
        tomatoes = _create_item(bucket, "Tomatoes", flagged=False)

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{tomatoes.id}/unflag/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        item = _get_item("Tomatoes")
        assert not item.flagged

    def test_item_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item_id = 9

        response = test_client.get(f"/bucket/{bucket.id}/item/{item_id}/unflag/")

        assert response.status_code == 404

    def test_bucket_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)
        bucket_id = 9

        response = test_client.get(f"/bucket/{bucket_id}/item/{item.id}/unflag/")

        assert response.status_code == 404


class TestDeleteItem:
    def test_delete_item(self, test_client):
        bucket = _create_bucket()
        tomatoes = _create_item(bucket, "Tomatoes")
        _create_item(bucket, "Carrots")

        response = test_client.get(
            f"/bucket/{bucket.id}/item/{tomatoes.id}/delete/",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"<td>Tomatoes</td>" not in response.data
        assert b"<td>Carrots</td>" in response.data
        assert Item.query.get(tomatoes.id) is None

    def test_item_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item_id = 9

        response = test_client.get(f"/bucket/{bucket.id}/item/{item_id}/delete/")

        assert response.status_code == 404

    def test_bucket_not_found__404_error(self, test_client):
        bucket = _create_bucket()
        item = _create_item(bucket)
        bucket_id = 9

        response = test_client.get(f"/bucket/{bucket_id}/item/{item.id}/delete/")

        assert response.status_code == 404


def _create_inbox_bucket():
    return _create_bucket(title="Inbox", description="Random things")


def _create_bucket(
    title="Shopping",
    description="Groceries we need",
    item_titles=None,
):
    bucket = Bucket(title=title, description=description)
    for item_title in item_titles or list():
        bucket.items.append(Item(title=item_title))
    db.session.add(bucket)
    db.session.commit()
    return bucket


def _create_item(bucket, title="Task", description=None, due_date=None, flagged=False):
    item = Item(
        bucket=bucket,
        title=title,
        description=description,
        due_date=due_date,
        flagged=flagged,
    )
    db.session.add(item)
    db.session.commit()
    return item


def _get_bucket(title):
    return db.session.query(Bucket).filter_by(title=title).first()


def _get_item(title):
    return db.session.query(Item).filter_by(title=title).first()
