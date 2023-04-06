from pydantic import BaseModel, root_validator, validator


class CSVConversionRequest(BaseModel):
    column_headers: list[str]
    data: list[str]

    @property
    def num_cols(self):
        return len(self.column_headers)

    @validator("data", pre=True)
    def convert_str_to_list(cls, value: str):
        return value.split(",")

    @root_validator
    def check_column_integrity(cls, values):
        column_headers = values.get("column_headers")
        num_columns = len(column_headers)
        data = values.get("data")
        if len(data) % num_columns != 0:
            raise ValueError(
                f"Uneven columns found. "
                f"Should be a multiple of {num_columns}. Found {len(data)}"
            )
        return values
