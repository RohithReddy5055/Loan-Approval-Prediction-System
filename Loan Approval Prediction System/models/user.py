from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='applicant')  # applicant, loan_officer, admin
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    applications = db.relationship('LoanApplication', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'
    
    def is_loan_officer(self):
        return self.role == 'loan_officer' or self.role == 'admin'