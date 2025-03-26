from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


def update_schema(
    schema: BaseModel, model: DeclarativeBase
) -> DeclarativeBase:
    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(model, key, value)
    return model
