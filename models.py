from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    persona_type = db.Column(db.String(50), nullable=False, default='custom') # salaried, student, freelancer, household, custom
    tagline = db.Column(db.String(200), default='')
    monthly_target_income = db.Column(db.Float, default=0.0)
    monthly_savings_target = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='$')
    avatar_color = db.Column(db.String(50), default='#6366f1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    budget_limits = db.relationship('BudgetLimit', backref='user', lazy=True, cascade='all, delete-orphan')
    saving_goals = db.relationship('SavingGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_logs = db.relationship('AIAdviceLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'persona_type': self.persona_type,
            'tagline': self.tagline,
            'monthly_target_income': self.monthly_target_income,
            'monthly_savings_target': self.monthly_savings_target,
            'currency': self.currency,
            'avatar_color': self.avatar_color,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), default='salary') # salary, freelance, allowance, investment, shared_family, bonus, other
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    is_recurring = db.Column(db.Boolean, default=True)
    notes = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source': self.source,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'is_recurring': self.is_recurring,
            'notes': self.notes
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False) # rent, food, groceries, transport, entertainment, utilities, healthcare, education, work_project, shopping, other
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    is_essential = db.Column(db.Boolean, default=True) # essential vs discretionary
    notes = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'is_essential': self.is_essential,
            'notes': self.notes
        }

class BudgetLimit(db.Model):
    __tablename__ = 'budget_limits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'monthly_limit': self.monthly_limit
        }

class SavingGoal(db.Model):
    __tablename__ = 'saving_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), default='general') # emergency_fund, vacation, investment, education, home, tech
    icon = db.Column(db.String(30), default='target')

    def to_dict(self):
        progress_pct = round((self.current_amount / self.target_amount * 100), 1) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_pct': min(100.0, progress_pct),
            'target_date': self.target_date,
            'category': self.category,
            'icon': self.icon
        }

class AIAdviceLog(db.Model):
    __tablename__ = 'ai_advice_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False) # user or assistant
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'message': self.message,
            'category': self.category,
            'timestamp': self.timestamp.strftime('%H:%M • %b %d') if self.timestamp else ''
        }
