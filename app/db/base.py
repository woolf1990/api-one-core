# import models so they are registered with SQLAlchemy metadata
from app.db.base_class import Base
from app.models import user
from app.models import file_model
from app.models import file_validation
from app.models import data_row
from app.models import document

# create tables if needed
def init_db(engine):
    Base.metadata.create_all(bind=engine)
