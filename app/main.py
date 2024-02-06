from PyPDF2 import PdfFileReader, PdfReader
from importers.file_importer import FileImporter
from s3.s3_client import S3Client
from repository.collection_repository import CollectionRepository
from pdf.adobe_pdf_service import AdobePDFService
import os
import pathlib
from datetime import date
from io import BytesIO

def run_adobe():
    print('Hello world')

    file_importer = FileImporter()
    s3_client = S3Client(
        aws_access_key_id='test',
        aws_secret_access_key='test',
        aws_endpoint='http://localhost:4566',
        aws_region_name='us-east-1')
    
    repository = CollectionRepository(
        path='chroma_data/'
    )

    # Bronze layer start

    # create file path
    path = file_importer.get_file_path('files', 'usa_vacation.pdf')

    # upload file
    s3_client.try_upload_file(path, 'bronze-1', 'usa_vacation.pdf')

    # Bronze layer end

    # Silver layer start
    files = s3_client.get_files_in_bucket('bronze-1')

    pdf_lines: [str] = []

    for file in files:
        fs = s3_client.get_file(file.bucket_name, file.key)

        reader = PdfReader(BytesIO(fs.read()))

        pages = len(reader.pages)
        for page, _ in enumerate(range(pages)):
            page = reader.pages[page]
            text = page.extract_text()

            pdf_lines = pdf_lines + text.splitlines()

    print(pdf_lines)

    repository.create_collection(collection_name='documents')

    print('Inserting data')
    repository.add(pdf_lines)

    print('Querying data')

    result = repository.get('Tell me something about new employees!')

    print(result['documents'])
    return

    client = S3Client(
        aws_access_key_id='test',
        aws_secret_access_key='test',
        aws_endpoint='http://localhost:4566',
        aws_region_name='us-east-1')

    client.get_buckets()

    return

    repository = CollectionRepository(
        path='chroma_data/'
    )

    documents = [
       "The latest iPhone model comes with impressive features and a powerful camera.",
        "Exploring the beautiful beaches and vibrant culture of Bali is a dream for many travelers.",
        "Einstein's theory of relativity revolutionized our understanding of space and time.",
        "Traditional Italian pizza is famous for its thin crust, fresh ingredients, and wood-fired ovens.",
        "The American Revolution had a profound impact on the birth of the United States as a nation.",
        "Regular exercise and a balanced diet are essential for maintaining good physical health.",
        "Leonardo da Vinci's Mona Lisa is considered one of the most iconic paintings in art history.",
        "Climate change poses a significant threat to the planet's ecosystems and biodiversity.",
        "Startup companies often face challenges in securing funding and scaling their operations.",
        "Beethoven's Symphony No. 9 is celebrated for its powerful choral finale, 'Ode to Joy.'",
    ]

    print('Creating collection')
    repository.create_collection(collection_name='documents')

    print('Inserting data')
    repository.add(documents)

    print('Querying data')

    result = repository.get('Find me some delicious food!')

    print(result['documents'])
    # adobe = AdobePDFService(
    #     client_id="...",
    #     client_secret="...",
    # )

    # assets = adobe.process_pdf(
    #     pdf_path=pathlib.Path(
    #         os.path.join(
    #             pathlib.Path(__file__).parent,
    #             "files",
    #             "sick_leave_policy.pdf",
    #         )
    #     )
    # )

    # print(assets)


if __name__ == "__main__":
    run_adobe()
