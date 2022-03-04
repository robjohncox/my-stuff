from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from src.database import Bucket


def bucket_title_is_unique(form, field):
    if field.object_data is not None:
        all_bucket_titles = {
            bucket.title for bucket in Bucket.query.all() if bucket.title != field.object_data
        }
    else:
        all_bucket_titles = {bucket.title for bucket in Bucket.query.all()}
    if field.data in all_bucket_titles:
        raise ValidationError("Bucket title must be unique.")


class BucketFormMixin(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Enter a title."),
            Length(max=32, message="No longer than 32 characters."),
            bucket_title_is_unique,
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(message="Enter a description.")],
    )


class CreateBucketForm(BucketFormMixin, FlaskForm):
    submit = SubmitField("Create bucket")


class UpdateBucketForm(BucketFormMixin, FlaskForm):
    submit = SubmitField("Update bucket")


class QuickCreateItemForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Enter a title."),
            Length(max=128, message="No longer than 128 characters."),
        ],
    )
    submit = SubmitField("Create")


class ItemFormMixin:
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Enter a title."),
            Length(max=128, message="No longer than 128 characters."),
        ],
    )
    description = TextAreaField("Description")
    due_date = DateField(
        "Due",
        format="%Y-%m-%d",
        validators=[Optional()],
        render_kw={"placeholder": "YYYY-MM-DD"},
    )
    flagged = BooleanField("Flagged?", default=False)


class CreateItemForm(ItemFormMixin, FlaskForm):
    submit = SubmitField("Create item")


class UpdateItemForm(ItemFormMixin, FlaskForm):
    submit = SubmitField("Update item")
