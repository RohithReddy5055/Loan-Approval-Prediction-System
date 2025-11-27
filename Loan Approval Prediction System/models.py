from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('LoanApplication', backref='applicant', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoanApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)  # education, home, car, personal, business
    amount = db.Column(db.Float, nullable=False)
    term = db.Column(db.Integer, nullable=False)  # in months
    purpose = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, processing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Applicant details
    applicant_name = db.Column(db.String(100), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    employment_status = db.Column(db.String(50))
    annual_income = db.Column(db.Float)
    credit_score = db.Column(db.Integer)
    
    # Additional details (can be stored as JSON for flexibility)
    additional_data = db.Column(db.JSON)
    
    # Admin notes
    admin_notes = db.Column(db.Text)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'loan_type': self.loan_type,
            'amount': self.amount,
            'term': self.term,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'applicant_name': self.applicant_name,
            'applicant_email': self.applicant_email,
            'phone_number': self.phone_number
        }

    def __repr__(self):
        return f"<LoanApplication {self.id} - {self.applicant_name}>"
