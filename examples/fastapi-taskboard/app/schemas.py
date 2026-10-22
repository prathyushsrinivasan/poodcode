from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints, model_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Username = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9_]{3,50}$"),
    BeforeValidator(lambda value: value.strip().lower() if isinstance(value, str) else value),
]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreate(InputModel):
    username: Username
    password: str = Field(min_length=12, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class TaskCreate(InputModel):
    title: Title


class TaskPatch(InputModel):
    title: Title | None = None
    done: bool | None = None

    @model_validator(mode="after")
    def forbid_explicit_null(self):
        if any(getattr(self, name) is None for name in self.model_fields_set):
            raise ValueError("Omit unchanged fields; null is not allowed")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    done: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
