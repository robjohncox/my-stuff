from datetime import date, datetime, timedelta

from flask import abort, Blueprint, redirect, render_template

from src.database import db, Bucket, Item
from src.forms import (
    CreateBucketForm,
    CreateItemForm,
    QuickCreateItemForm,
    UpdateBucketForm,
    UpdateItemForm,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    inbox = db.session.query(Bucket).filter_by(title="Inbox").first()
    if inbox is None:
        abort(404)
    return redirect(f"/bucket/{inbox.id}/")


@bp.route("/bucket/<bucket_id>/", methods=["GET", "POST"])
def bucket(bucket_id):
    bucket = _get_bucket(bucket_id)
    form = QuickCreateItemForm()
    if form.validate_on_submit():
        item = Item(title=form.title.data)
        bucket.items.append(item)
        db.session.add(bucket)
        db.session.commit()
    all_buckets = Bucket.query.order_by("id")
    return render_template(
        "bucket.html",
        title=bucket.title,
        bucket=bucket,
        all_buckets=all_buckets,
        form=form,
    )


@bp.route("/bucket/create/", methods=["GET", "POST"])
def create_bucket():
    form = CreateBucketForm()
    if form.validate_on_submit():
        bucket = Bucket(
            title=form.title.data,
            description=form.description.data,
        )
        db.session.add(bucket)
        db.session.commit()
        return redirect(f"/bucket/{bucket.id}/")
    else:
        all_buckets = Bucket.query.order_by("id")
        return render_template(
            "update_bucket.html",
            title="Create new bucket",
            all_buckets=all_buckets,
            form=form,
        )


@bp.route("/bucket/<bucket_id>/update/", methods=["GET", "POST"])
def update_bucket(bucket_id):
    bucket = _get_bucket(bucket_id)
    form = UpdateBucketForm(obj=bucket)
    if form.validate_on_submit():
        bucket.title = form.title.data
        bucket.description = form.description.data
        db.session.add(bucket)
        db.session.commit()
        return redirect(f"/bucket/{bucket.id}/")
    else:
        all_buckets = Bucket.query.order_by("id")
        return render_template(
            "update_bucket.html",
            title="Create new bucket",
            all_buckets=all_buckets,
            form=form,
        )


@bp.route("/bucket/<bucket_id>/item/create/", methods=["GET", "POST"])
def create_item(bucket_id):
    bucket = _get_bucket(bucket_id)
    form = CreateItemForm()
    if form.validate_on_submit():
        item = Item(
            title=form.title.data,
            description=form.description.data or None,
            due_date=form.due_date.data,
            flagged=form.flagged.data,
        )
        bucket.items.append(item)
        db.session.add(bucket)
        db.session.commit()
        return redirect(f"/bucket/{bucket.id}/")
    else:
        all_buckets = Bucket.query.order_by("id")
        return render_template(
            "update_item.html",
            title=f"Create new item in {bucket.title}",
            bucket=bucket,
            all_buckets=all_buckets,
            form=form,
        )


@bp.route("/bucket/<bucket_id>/item/<item_id>/update/", methods=["GET", "POST"])
def update_item(bucket_id, item_id):
    bucket = _get_bucket(bucket_id)
    item = _get_item(item_id)
    form = UpdateItemForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.description = form.description.data or None
        item.due_date = form.due_date.data
        item.flagged = form.flagged.data
        db.session.add(item)
        db.session.commit()
        return redirect(f"/bucket/{bucket.id}/")
    else:
        all_buckets = Bucket.query.order_by("id")
        return render_template(
            "update_item.html",
            title=f"Update item in {bucket.title}",
            bucket=bucket,
            all_buckets=all_buckets,
            form=form,
        )


@bp.route("/bucket/<bucket_id>/item/<item_id>/complete/")
def complete_item(bucket_id, item_id):
    bucket = _get_bucket(bucket_id)
    item = _get_item(item_id)
    item.completed_time = datetime.utcnow()
    db.session.add(item)
    db.session.commit()
    return redirect(f"/bucket/{bucket.id}/")


@bp.route("/bucket/<bucket_id>/item/<item_id>/due_date_plus_one_day/")
def item_due_date_plus_one_day(bucket_id, item_id):
    bucket = _get_bucket(bucket_id)
    item = _get_item(item_id)
    updated_due_date = item.due_date or date.today()
    updated_due_date += timedelta(days=1)
    item.due_date = updated_due_date
    db.session.add(item)
    db.session.commit()
    return redirect(f"/bucket/{bucket.id}/")


@bp.route("/bucket/<bucket_id>/item/<item_id>/flag/")
def flag_item(bucket_id, item_id):
    bucket = _get_bucket(bucket_id)
    item = _get_item(item_id)
    item.flagged = True
    db.session.add(item)
    db.session.commit()
    return redirect(f"/bucket/{bucket.id}/")


@bp.route("/bucket/<bucket_id>/item/<item_id>/unflag/")
def unflag_item(bucket_id, item_id):
    bucket = _get_bucket(bucket_id)
    item = _get_item(item_id)
    item.flagged = False
    db.session.add(item)
    db.session.commit()
    return redirect(f"/bucket/{bucket.id}/")


@bp.route("/bucket/<bucket_id>/item/<item_id>/delete/")
def delete_item(bucket_id, item_id):
    bucket = _get_bucket(bucket_id)
    item = _get_item(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(f"/bucket/{bucket.id}/")


def _get_bucket(bucket_id):
    bucket = Bucket.query.get(bucket_id)
    if bucket is None:
        abort(404)
    return bucket


def _get_item(item_id):
    item = Item.query.get(item_id)
    if item is None:
        abort(404)
    return item
