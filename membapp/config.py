class Config:
    ADMIN_EMAIL="test@memba.com"
    SECRET_KEY='4P)lD710k'
    
class LiveConfig(Config):
    ADMIN_EMAIL="admin@memba.com"
    SERVER_ADDRESS="https://server.memba.com"
    
class TestConfig(Config):
    SERVER_ADDRESS="http://127.0.0.1:5000"
    