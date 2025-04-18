from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # admin, commercial, director, accountant
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    projects = db.relationship('Project', backref='client', lazy=True)
    invoices = db.relationship('Invoice', backref='client', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, pending, approved, in_progress, completed
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='project', lazy=True)
    quotations = db.relationship('Quotation', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, sent, approved, rejected
    total_amount = db.Column(db.Float, nullable=False)
    valid_until = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('QuotationItem', backref='quotation', lazy=True)

class QuotationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id'), nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue
    total_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payment', backref='invoice', lazy=True)
    export_status = db.Column(db.String(20), default='pending')  # pending, exported, failed

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(20))  # bank_transfer, check, cash
    reference = db.Column(db.String(50))
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    export_status = db.Column(db.String(20), default='pending')  # pending, exported, failed

class ERPExport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # invoice, payment
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    record_id = db.Column(db.Integer, nullable=False)  # ID of invoice or payment
    export_date = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)