from sqlmodel import create_engine, SQLModel

engine = create_engine("sqlite:///todo.db", echo=False)

def create_db():
    SQLModel.metadata.create_all(engine)