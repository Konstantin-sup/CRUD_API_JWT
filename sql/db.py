from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:1488fa@localhost:3306/traning_schema",
    echo=True,
)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


#filling_func(session)
#data = select_data(session,"admin_tw")

#del_data(session)
#insert_data(session)

