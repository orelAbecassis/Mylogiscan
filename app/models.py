from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association Tables
intervenant_services = db.Table('intervenant_services',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)

intervenant_clients = db.Table('intervenant_clients',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='intervenant') # admin, client, intervenant
    
    # Relationships
    interventions = db.relationship('Intervention', backref='intervenant', lazy='dynamic', foreign_keys='Intervention.intervenant_id')
    
    # Many-to-Many
    services = db.relationship('Service', secondary=intervenant_services, lazy='subquery',
        backref=db.backref('intervenants', lazy=True))
    clients = db.relationship('Client', secondary=intervenant_clients, lazy='subquery',
        backref=db.backref('assigned_intervenants', lazy=True))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Link to a User account if they have login
    interventions = db.relationship('Intervention', backref='client', lazy='dynamic')

    def __repr__(self):
        return f'<Client {self.name}>'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., Ménage, Baby-sitting
    
    interventions = db.relationship('Intervention', backref='service', lazy='dynamic')

    def __repr__(self):
        return f'<Service {self.name}>'

class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default='Scheduled') # Scheduled, Completed, DeletionRequested
    cancellation_reason = db.Column(db.String(255))
    
    intervenant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

    def __repr__(self):
        return f'<Intervention {self.id}>'
