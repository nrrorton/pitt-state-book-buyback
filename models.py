from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Users Model
class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    display_name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    # is_active column to allow for account suspension without deletion
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships with users
    listings = db.relationship('Listing', backref='seller', lazy=True, foreign_keys='Listing.seller_id')

    ratings_received = db.relationship('Rating', backref='seller', lazy=True, foreign_keys='Rating.seller_id')

    reports_made = db.relationship('Report', backref='reporter', lazy=True, foreign_keys='Report.reporter_id')

    # Helper methods on the model for ease of use elsewhere
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Method calculating the average rating of a user
    def average_rating(self):
        if not self.ratings_received:
            return None
        return round(sum(r.score for r in self.ratings_received) / len(self.ratings_received), 1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'member_since': self.created_at.strftime('%B %Y'),
            'average_rating': self.average_rating(),
            'listing_ccount': len(self.listings)
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
    
# Book Listings Model
class Listing(db.Model):

    __tablename__ = 'listings'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    edition = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Float, nullable=False)
    course_code = db.Column(db.String(20), nullable=True)
    professor = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships with Listings
    ratings = db.relationship('Rating', backref='listing', lazy=True)
    reports = db.relationship('Report', backref='listing', lazy=True, foreign_keys='Report.listing_id')

    def __repr__(self):
        return f'<Listing {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'edition': self.edition,
            'condition': self.condition,
            'price': self.price,
            'course_code': self.course_code,
            'professor': self.professor,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': f'/static/uploads/{self.image_filename}' if self.image_filename else None,
            'seller': self.seller.to_dict()
        }
    

# Rating Model
class Rating(db.Model):

    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable = False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Rating {self.score} for listing {self.listing_id}>'
    

# Report Model
class Report(db.Model):

    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Report by user {self.reporter_id}>'