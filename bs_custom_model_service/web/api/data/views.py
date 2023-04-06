import io
from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from bs_custom_model_service.web.api.models.request.csv_conversion import (
    CSVConversionRequest,
)
from io import StringIO
import pandas as pd
import numpy as np

router = APIRouter()


@router.post("/csv")
def convert_to_csv(csv_conversion_request: CSVConversionRequest) -> StreamingResponse:
    """
    Converts a string into csv

    :param csv_conversion_request: S
    """
    df = pd.DataFrame(
        np.array(csv_conversion_request.data).reshape(
            -1, csv_conversion_request.num_cols
        ),
        columns=csv_conversion_request.column_headers,
    )
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=converted.csv"
    return response
