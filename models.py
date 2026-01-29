from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(150), nullable=False)
    status = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100))
    priority = db.Column(db.String(50))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name
