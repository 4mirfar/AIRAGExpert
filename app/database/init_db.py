from app.database.database import Base, engine
from app.database.models import DocumentDB


def init_db():
    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_db()