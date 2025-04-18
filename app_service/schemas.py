from pydantic import BaseModel, ConfigDict


class Proba(BaseModel):
    pass


class ProbaCreate(Proba):
    name: str # = Field(example="Что-то очень интересное!!!")

    # class Config:
    #     orm_mode = True
    #     # не работает как надо
    #     model_config = {
    #         "json_schema_extra": {
    #             "examples": [{
    #                 "id": 1,
    #                 "name": "Что-то очень интересное",
    #             }]
    #         }
    #     }


class ProbaGetAll(Proba):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )

