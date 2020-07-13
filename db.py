from config import config as settings
from sqlalchemy import create_engine

def engine():
    s = "mysql+pymysql://%s:%s@%s/%s" % (settings()['mysql_user'], settings()['mysql_password'], settings()['mysql_host'], settings()['mysql_database'])
    engine = create_engine(s)

    return engine
