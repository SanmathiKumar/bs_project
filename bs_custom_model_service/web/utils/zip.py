import io
import os
import zipfile


def create_zip_from_folder_inmem(folder_path) -> io.BytesIO:
    """
    Zips a folder and all its contents.

    :param folder_path: The path to the folder to zip
    :return: The zip file as a StringIO object
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                arcname = os.path.join(os.path.relpath(root, folder_path), file)
                zip_file.write(os.path.join(root, file), arcname)

    return zip_buffer
