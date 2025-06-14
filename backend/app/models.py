# backend/app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    picture_url = db.Column(db.String(250), nullable=True)
    steam_id = db.Column(db.String(50), unique=True, nullable=True)
    retro_username = db.Column(db.String(80), unique=True, nullable=True)
    total_xp = db.Column(db.Integer, nullable=False, default=0)
    total_coins = db.Column(db.Integer, nullable=False, default=0)
    equipped_banner_url = db.Column(db.String(255), nullable=True)
    
    platinados = db.relationship('Platinado', backref='user', lazy=True)
    inventory = db.relationship('UserInventory', backref='owner', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), 
        lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def __repr__(self):
        return f'<User {self.name}>'
        

class Platinado(db.Model):
    __tablename__ = 'platinado'
    id = db.Column(db.Integer, primary_key=True)
    game_appid = db.Column(db.Integer, nullable=False)
    game_name = db.Column(db.String(200), nullable=False)
    achieved_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    platform = db.Column(db.String(50), nullable=False, default='steam')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False, default='Padrão')
    xp_value = db.Column(db.Integer, nullable=False, default=10)
    platform = db.Column(db.String(50), nullable=False, default='steam')
    coin_value = db.Column(db.Integer, nullable=False, default=5)

# --- MODELOS DA LOJA UNIFICADOS ---

class ShopItem(db.Model):
    __tablename__ = 'shop_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_coins = db.Column(db.Integer, nullable=False)
    
    # Tipos de item: 'GAME_KEY', 'BANNER', 'AVATAR_BORDER', etc.
    item_type = db.Column(db.String(50), nullable=False)
    # Valor do item, ex: a URL da imagem para um banner. Não é necessário para chaves.
    value = db.Column(db.String(255), nullable=True)
    # AppID do jogo relacionado, para puxar a imagem do item na loja
    appid = db.Column(db.Integer, nullable=True)
    
    # Relacionamento para acessar as chaves de um item (se for do tipo GAME_KEY)
    keys = db.relationship('ItemKey', backref='item', lazy=True)

class UserInventory(db.Model):
    __tablename__ = 'user_inventory'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=False)
    acquired_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    item = db.relationship('ShopItem')

class ItemKey(db.Model):
    __tablename__ = 'item_key'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=False)
    key_value = db.Column(db.String(100), unique=True, nullable=False)
    is_redeemed = db.Column(db.Boolean, default=False, nullable=False)
    redeemed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    redeemed_at = db.Column(db.DateTime, nullable=True)