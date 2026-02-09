from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://logistics:logistics@localhost:5432/logistics_db"

engine = create_engine(DATABASE_URL, echo=False)
