from sqlmodel import SQLModel, create_engine, Session

# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL = "postgresql+psycopg2://postgres:password123@localhost/chat-app"
engine = create_engine(DATABASE_URL, echo=True) 

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session   