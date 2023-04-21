import io
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, File
import numpy as np
import pandas as pd
from fastapi import APIRouter, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse
import os
import subprocess

from bs_custom_model_service.web.api.models.request.csv_conversion import (
    CSVConversionRequest,
)
from bs_custom_model_service.web.core.execute import run_command, ExecutionFailedError

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


@router.post("/exec")
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

@router.post("/script and data file/")
async def process_data(script: UploadFile, data: UploadFile):

    # Save the data file to a temporary directory
    data_contents = await data.read()
    with tempfile.TemporaryDirectory() as tempdir:
        data_file = Path(tempdir) / f"{uuid.uuid4()}.json"
        data_file.write_bytes(data_contents)

    # Save the script file to a temporary directory
    script_contents = await script.read()
    with tempfile.TemporaryDirectory() as tempdir:
        script_file = Path(tempdir) / f"{uuid.uuid4()}.py"
        script_file.write_bytes(script_contents)


    # Run the script file on the data file
    # cmd = f"python {script_file} {data_file}"
    # output = subprocess.check_output(cmd, shell=True, text=True)
    #
    # return {"output": output}
        try:
            output = run_command(["python", script_file.as_posix()])
            response = {"output": output, "is_exception_raised": False}
        except ExecutionFailedError as e:
            response = {"output": str(e), "is_exception_raised": True}
    return JSONResponse(content=jsonable_encoder(response))

@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "contents": contents}


