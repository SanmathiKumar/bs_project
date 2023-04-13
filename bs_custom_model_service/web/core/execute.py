from __future__ import annotations

import logging
from subprocess import Popen, PIPE
from typing import List, Tuple

logger = logging.getLogger("bs.core.execute")


class ExecutionFailedError(Exception):
    """
    Raised when a command fails to execute
    """

    pass


def run_command(command: str | List | Tuple, verbose=True, shell=True):
    """
    Run a command in a subprocess.
    Args:
        command: Command to run.
        verbose: Log the command output. Defaults to True.
        shell: If true, the command will be executed through the shell. Defaults to True.
    Returns:
        The output of the command.
    >>> run_command("echo 'hello world'")
    'hello world'
    """
    if isinstance(command, (list, tuple)):
        command = " ".join(command)

    logger.debug(f"Running command: {command}")

    output, error = "", ""
    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=shell)
    for line in iter(proc.stdout.readline, b""):
        if verbose:
            logger.info(line.decode())
        output += line.decode()
    for line in iter(proc.stderr.readline, b""):
        if verbose:
            logger.error(line.decode())
        error += line.decode()
    proc.stdout.close()
    proc.stderr.close()
    ret_code = proc.wait()
    if ret_code == 1:
        raise ExecutionFailedError(error)
    return output
