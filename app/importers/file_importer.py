import os
import pathlib


class FileImporter:
    def __init__(self):
        pass

    def get_file_path(self, folder: str, name: str):

        pdf_path = pathlib.Path(
            os.path.join(
                os.getcwd(),
                "app",
                folder,
                name,
            )
        )

        return pdf_path