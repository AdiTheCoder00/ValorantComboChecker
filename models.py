from app import db
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from datetime import datetime
import json

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # valid, invalid, error
    
    # Account Intelligence Data
    rank = Column(String(50))
    region = Column(String(10))
    level = Column(Integer)
    competitive_rank = Column(String(30))
    rr_points = Column(Integer)  # Rank Rating points
    peak_rank = Column(String(30))
    
    # Inventory & Value Data
    skins_count = Column(Integer, default=0)
    knife_skins = Column(Text)  # JSON string of knife skins
    premium_skins = Column(Text)  # JSON string of premium skins
    battle_pass_level = Column(Integer)
    valorant_points = Column(Integer, default=0)
    estimated_value = Column(Float, default=0.0)
    
    # Account History
    last_match_date = Column(DateTime)
    total_matches = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    hours_played = Column(Float, default=0.0)
    
    # Security & Detection
    two_factor_enabled = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    creation_date = Column(DateTime)
    last_login = Column(DateTime)
    
    # Technical Data
    response_time = Column(Float)
    session_id = Column(String(100))
    check_timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'status': self.status,
            'rank': self.rank,
            'region': self.region,
            'level': self.level,
            'competitive_rank': self.competitive_rank,
            'rr_points': self.rr_points,
            'skins_count': self.skins_count,
            'estimated_value': self.estimated_value,
            'knife_skins': json.loads(self.knife_skins) if self.knife_skins else [],
            'premium_skins': json.loads(self.premium_skins) if self.premium_skins else [],
            'last_match_date': self.last_match_date.isoformat() if self.last_match_date else None,
            'total_matches': self.total_matches,
            'win_rate': self.win_rate,
            'hours_played': self.hours_played,
            'two_factor_enabled': self.two_factor_enabled,
            'phone_verified': self.phone_verified,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None
        }

class SkinData(db.Model):
    __tablename__ = 'skin_data'
    
    id = Column(Integer, primary_key=True)
    skin_name = Column(String(200), unique=True, nullable=False)
    weapon_type = Column(String(50))
    skin_tier = Column(String(30))  # Select, Deluxe, Premium, Ultra
    price_vp = Column(Integer)  # Valorant Points price
    market_value = Column(Float)  # Estimated market value in USD
    rarity_score = Column(Integer)  # 1-10 rarity rating
    is_knife = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    release_date = Column(DateTime)
    
    def to_dict(self):
        return {
            'skin_name': self.skin_name,
            'weapon_type': self.weapon_type,
            'skin_tier': self.skin_tier,
            'price_vp': self.price_vp,
            'market_value': self.market_value,
            'rarity_score': self.rarity_score,
            'is_knife': self.is_knife,
            'is_premium': self.is_premium
        }

class CheckingSession(db.Model):
    __tablename__ = 'checking_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    total_checked = Column(Integer, default=0)
    valid_count = Column(Integer, default=0)
    invalid_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Intelligence Summary
    high_value_accounts = Column(Integer, default=0)  # Accounts worth >$100
    premium_accounts = Column(Integer, default=0)     # Accounts with premium skins
    ranked_accounts = Column(Integer, default=0)      # Accounts with competitive rank
    
    average_account_value = Column(Float, default=0.0)
    total_estimated_value = Column(Float, default=0.0)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_checked': self.total_checked,
            'valid_count': self.valid_count,
            'high_value_accounts': self.high_value_accounts,
            'premium_accounts': self.premium_accounts,
            'average_account_value': self.average_account_value,
            'total_estimated_value': self.total_estimated_value
        }