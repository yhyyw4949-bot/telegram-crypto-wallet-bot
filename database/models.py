"""
Database models for the wallet bot using SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    usdt_balance = Column(Float, default=0.0)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wallets = relationship('Wallet', back_populates='user', cascade='all, delete-orphan')
    transactions = relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    transfers_sent = relationship('InternalTransfer', back_populates='sender', foreign_keys='InternalTransfer.sender_id')
    transfers_received = relationship('InternalTransfer', back_populates='receiver', foreign_keys='InternalTransfer.receiver_id')

class Wallet(Base):
    """Wallet model"""
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    wallet_address = Column(String(255), unique=True, nullable=False, index=True)
    private_key_encrypted = Column(Text, nullable=False)  # Encrypted private key
    public_key = Column(String(255))
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='wallets')
    transactions = relationship('Transaction', back_populates='wallet', cascade='all, delete-orphan')

class Transaction(Base):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=True, index=True)
    tx_hash = Column(String(255), unique=True, nullable=False, index=True)
    tx_type = Column(String(50), nullable=False)  # deposit, withdrawal
    amount = Column(Float, nullable=False)
    from_address = Column(String(255))
    to_address = Column(String(255))
    status = Column(String(50), default='pending')  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    gas_fee = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    confirmed_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    user = relationship('User', back_populates='transactions')
    wallet = relationship('Wallet', back_populates='transactions')

class InternalTransfer(Base):
    """Internal transfer model (P2P transfers without blockchain)"""
    __tablename__ = 'internal_transfers'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default='completed')
    transfer_reference = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    
    # Relationships
    sender = relationship('User', back_populates='transfers_sent', foreign_keys=[sender_id])
    receiver = relationship('User', back_populates='transfers_received', foreign_keys=[receiver_id])

class AdminLog(Base):
    """Admin action log model"""
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=False, index=True)
    action = Column(String(255), nullable=False)  # add_balance, subtract_balance, etc.
    target_user_id = Column(Integer, ForeignKey('users.id'), index=True)
    amount = Column(Float)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class RateLimit(Base):
    """Rate limiting model"""
    __tablename__ = 'rate_limits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # message, withdraw, transfer
    count = Column(Integer, default=0)
    reset_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
