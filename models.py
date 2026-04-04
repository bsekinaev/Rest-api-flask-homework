from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db =SQLAlchemy()

class Ads(db.Model):
    __tablename__='ads'
    id=db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(100), nullable=False)
    description=db.Column(db.Text, nullable=False)
    created_at= db.Column(db.DateTime(), default=datetime.utcnow)
    owner = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title' :self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'owner': self.owner
        }
