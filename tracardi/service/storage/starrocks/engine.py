from sqlalchemy import create_engine

engine = create_engine('starrocks://username:password@host:port/database')