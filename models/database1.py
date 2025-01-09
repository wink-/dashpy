from . import db
from .base import BaseModel

class ExampleTable(BaseModel):
    """Example model for a table in database1"""
    __tablename__ = 'example_table'
    __bind_key__ = 'database1'  # This tells SQLAlchemy which database to use
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Add relationships if needed
    # related_items = db.relationship('RelatedModel', backref='example_table')
