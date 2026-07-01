"""
Repository layer for database operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import Optional, List
import logging
from .models import User, Wallet, Transaction, InternalTransfer, AdminLog, RateLimit

logger = logging.getLogger(__name__)

class UserRepository:
    """User repository for database operations"""
    
    @staticmethod
    def get_or_create(db: Session, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
        """Get existing user or create new one"""
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.add(user)
            db.commit()
            logger.info(f"✓ New user created: {telegram_id}")
        else:
            user.last_activity = datetime.utcnow()
            user.username = username or user.username
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            db.commit()
        return user
    
    @staticmethod
    def get_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_all(db: Session) -> List[User]:
        """Get all users"""
        return db.query(User).all()
    
    @staticmethod
    def update_balance(db: Session, user_id: int, amount: float) -> bool:
        """Update user balance"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.usdt_balance += amount
                user.updated_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to update balance: {e}")
            db.rollback()
        return False
    
    @staticmethod
    def set_balance(db: Session, user_id: int, amount: float) -> bool:
        """Set user balance to exact amount"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.usdt_balance = amount
                user.updated_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to set balance: {e}")
            db.rollback()
        return False
    
    @staticmethod
    def ban_user(db: Session, user_id: int) -> bool:
        """Ban user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_banned = True
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to ban user: {e}")
            db.rollback()
        return False
    
    @staticmethod
    def unban_user(db: Session, user_id: int) -> bool:
        """Unban user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_banned = False
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to unban user: {e}")
            db.rollback()
        return False
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user and all related data"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to delete user: {e}")
            db.rollback()
        return False

class WalletRepository:
    """Wallet repository for database operations"""
    
    @staticmethod
    def create(db: Session, user_id: int, wallet_address: str, private_key_encrypted: str, public_key: str = None) -> Wallet:
        """Create new wallet"""
        wallet = Wallet(
            user_id=user_id,
            wallet_address=wallet_address,
            private_key_encrypted=private_key_encrypted,
            public_key=public_key
        )
        db.add(wallet)
        db.commit()
        logger.info(f"✓ Wallet created: {wallet_address}")
        return wallet
    
    @staticmethod
    def get_by_address(db: Session, address: str) -> Optional[Wallet]:
        """Get wallet by address"""
        return db.query(Wallet).filter(Wallet.wallet_address == address).first()
    
    @staticmethod
    def get_user_wallets(db: Session, user_id: int) -> List[Wallet]:
        """Get all wallets of a user"""
        return db.query(Wallet).filter(Wallet.user_id == user_id).all()
    
    @staticmethod
    def count_user_wallets(db: Session, user_id: int) -> int:
        """Count wallets of a user"""
        return db.query(Wallet).filter(Wallet.user_id == user_id).count()
    
    @staticmethod
    def update_balance(db: Session, wallet_id: int, amount: float) -> bool:
        """Update wallet balance"""
        try:
            wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if wallet:
                wallet.balance += amount
                wallet.last_activity = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to update wallet balance: {e}")
            db.rollback()
        return False
    
    @staticmethod
    def delete(db: Session, wallet_id: int) -> bool:
        """Delete wallet"""
        try:
            wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
            if wallet:
                db.delete(wallet)
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to delete wallet: {e}")
            db.rollback()
        return False

class TransactionRepository:
    """Transaction repository for database operations"""
    
    @staticmethod
    def create(db: Session, user_id: int, wallet_id: int, tx_hash: str, tx_type: str, amount: float, 
               from_address: str = None, to_address: str = None) -> Transaction:
        """Create new transaction"""
        transaction = Transaction(
            user_id=user_id,
            wallet_id=wallet_id,
            tx_hash=tx_hash,
            tx_type=tx_type,
            amount=amount,
            from_address=from_address,
            to_address=to_address
        )
        db.add(transaction)
        db.commit()
        return transaction
    
    @staticmethod
    def get_by_hash(db: Session, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash"""
        return db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
    
    @staticmethod
    def get_user_transactions(db: Session, user_id: int, limit: int = 50) -> List[Transaction]:
        """Get user transaction history"""
        return db.query(Transaction).filter(Transaction.user_id == user_id).order_by(desc(Transaction.created_at)).limit(limit).all()
    
    @staticmethod
    def get_wallet_transactions(db: Session, wallet_id: int, limit: int = 50) -> List[Transaction]:
        """Get wallet transaction history"""
        return db.query(Transaction).filter(Transaction.wallet_id == wallet_id).order_by(desc(Transaction.created_at)).limit(limit).all()
    
    @staticmethod
    def update_status(db: Session, tx_hash: str, status: str, confirmations: int = 0) -> bool:
        """Update transaction status"""
        try:
            tx = db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
            if tx:
                tx.status = status
                tx.confirmations = confirmations
                if status == 'confirmed':
                    tx.confirmed_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"✗ Failed to update transaction status: {e}")
            db.rollback()
        return False

class InternalTransferRepository:
    """Internal transfer repository for database operations"""
    
    @staticmethod
    def create(db: Session, sender_id: int, receiver_id: int, amount: float, transfer_reference: str) -> InternalTransfer:
        """Create new internal transfer"""
        transfer = InternalTransfer(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            transfer_reference=transfer_reference
        )
        db.add(transfer)
        db.commit()
        return transfer
    
    @staticmethod
    def get_user_transfers(db: Session, user_id: int, limit: int = 50) -> List[InternalTransfer]:
        """Get user transfer history (sent and received)"""
        transfers = db.query(InternalTransfer).filter(
            (InternalTransfer.sender_id == user_id) | (InternalTransfer.receiver_id == user_id)
        ).order_by(desc(InternalTransfer.created_at)).limit(limit).all()
        return transfers

class AdminLogRepository:
    """Admin log repository for database operations"""
    
    @staticmethod
    def log_action(db: Session, admin_id: int, action: str, target_user_id: int = None, amount: float = None, details: str = None) -> AdminLog:
        """Log admin action"""
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            target_user_id=target_user_id,
            amount=amount,
            details=details
        )
        db.add(log)
        db.commit()
        return log
    
    @staticmethod
    def get_logs(db: Session, limit: int = 100) -> List[AdminLog]:
        """Get admin logs"""
        return db.query(AdminLog).order_by(desc(AdminLog.created_at)).limit(limit).all()

class StatisticsRepository:
    """Statistics repository for database operations"""
    
    @staticmethod
    def get_total_users(db: Session) -> int:
        """Get total users count"""
        return db.query(User).count()
    
    @staticmethod
    def get_total_wallets(db: Session) -> int:
        """Get total wallets count"""
        return db.query(Wallet).count()
    
    @staticmethod
    def get_total_balance(db: Session) -> float:
        """Get total USDT balance stored"""
        result = db.query(func.sum(User.usdt_balance)).scalar()
        return result or 0.0
    
    @staticmethod
    def get_total_deposits(db: Session) -> float:
        """Get total deposit amount"""
        result = db.query(func.sum(Transaction.amount)).filter(Transaction.tx_type == 'deposit').scalar()
        return result or 0.0
    
    @staticmethod
    def get_total_withdrawals(db: Session) -> float:
        """Get total withdrawal amount"""
        result = db.query(func.sum(Transaction.amount)).filter(Transaction.tx_type == 'withdrawal').scalar()
        return result or 0.0
    
    @staticmethod
    def get_total_transfers(db: Session) -> float:
        """Get total internal transfer amount"""
        result = db.query(func.sum(InternalTransfer.amount)).scalar()
        return result or 0.0
