from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Import all models here
from .auth import User, UserSettings
from .calsys import *  # Import all calsys models
# Import your other database models here
# from .database1 import *
# from .database2 import *
