from datetime import date, datetime
from humanize import naturaldate

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Bucket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    can_deactivate = db.Column(db.Boolean, default=True, nullable=False)
    deactivated_time = db.Column(db.DateTime, nullable=True)

    @property
    def incomplete_items(self):
        return list(
            db.session.query(Item)
            .filter_by(bucket_id=self.id)
            .filter_by(completed_time=None)
            .order_by("id")
        )

    def __repr__(self):
        return f"<Bucket {self.id}: {self.title}>"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bucket_id = db.Column(db.Integer, db.ForeignKey("bucket.id"), nullable=False)
    bucket = db.relationship("Bucket", backref=db.backref("items", lazy=False))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    completed_time = db.Column(db.DateTime, nullable=True)
    flagged = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def due_date_human(self):
        if self.due_date is None:
            return None
        else:
            return f"{naturaldate(self.due_date).title()}"

    @property
    def is_overdue(self):
        if self.due_date is None:
            return False
        return self.due_date < date.today()

    def __repr__(self):
        return f"<Item {self.id}: {self.title}>"
