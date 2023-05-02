import io
import tempfile
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse, Response

from bs_custom_model_service.web.api.models.request.csv_conversion import (
    CSVConversionRequest,
)
from bs_custom_model_service.web.core.execute import run_command, ExecutionFailedError
from bs_custom_model_service.web.utils.zip import create_zip_from_folder_inmem

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


@router.post("/exec_no_input")
async def execute_python_script(file: UploadFile):
    """
    Executes any script uploaded as a python program.

    :param file: Uploaded py script.
    :return: Result of execution.
    """

    contents = await file.read()
    with tempfile.TemporaryDirectory() as tempdir:
        script_file = Path(tempdir) / f"{uuid.uuid4()}.py"
        script_file.write_bytes(contents)
        try:
            output = run_command(["python", script_file.as_posix()])
            response = {"output": output, "is_exception_raised": False}
        except ExecutionFailedError as e:
            response = {"output": str(e), "is_exception_raised": True}
    return JSONResponse(content=jsonable_encoder(response))


@router.post("/exec")
async def execute_python_script(script: UploadFile, input_file: UploadFile):
    """
    Executes any script uploaded as a python program.

    :param script: Uploaded py script.
    :param input_file: Uploaded input file.
    :return: Result of execution.
    """

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        if not script.filename.endswith(".py"):
            return Response(status_code=400, content={
                "message": "Invalid script file. Must be a .py file."})
        script_file = tempdir / f"{uuid.uuid4()}-{script.filename}"
        script_file.write_bytes(await script.read())
        input_file_path = tempdir / f"{uuid.uuid4()}-{input_file.filename}"
        input_file_path.write_bytes(await input_file.read())
        try:
            output = run_command(
                ["python", script_file.as_posix(), input_file_path.as_posix()]
            )
            headers = {"X-Script-Raised-Exception": "false"}
            with open(tempdir / f"{script_file.stem}_execution_output.txt", "w") as f:
                f.write(output)
        except ExecutionFailedError as e:
            headers = {"X-Script-Raised-Exception": "true"}
            with open(tempdir / f"{script_file.stem}_execution_output.txt", "w") as f:
                f.write(str(e))
        input_file_path.unlink()
        script_file.unlink()

        if len(list(tempdir.glob("*"))) == 0:
            return Response(headers=headers)
        zip_io = create_zip_from_folder_inmem(tempdir)
        response_object = Response(zip_io.getvalue(),
                                   media_type="application/x-zip-compressed",
                                   headers=headers)
        response_object.headers[
            'Content-Disposition'] = f'attachment; filename=result.zip'
        return response_object
