from typing import Optional, List

from pydantic import BaseModel


class PythonFileExecutionRequest(BaseModel):
    args: Optional[List[str]] = None
