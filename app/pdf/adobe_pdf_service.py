import pathlib
from typing import Optional

import httpx
from pydantic import BaseModel, AnyHttpUrl

from .adobe_pdf_token import AdobePDFServiceToken
from .exceptions import AdobePDFServiceJobException, AdobePDFServiceException
from .logger import logger

from time import sleep


class PreSignedURI(BaseModel):
    uploadUri: AnyHttpUrl
    assetID: str


class JobStatusContent(BaseModel):
    downloadUri: AnyHttpUrl
    assetID: str


class JobResult(BaseModel):
    version: dict
    extended_metadata: dict
    elements: list[dict]
    pages: list[dict]


class JobStatus(BaseModel):
    status: str
    content: Optional[JobStatusContent] = None

    def is_done(self) -> bool:
        return self.status == "done"

    def is_progress(self):
        return self.status == "in progress"

    def is_failed(self):
        return self.status == "failed"


class AdobePDFService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: AdobePDFServiceToken = AdobePDFServiceToken(
            client_id=self._client_id,
            client_secret=self._client_secret,
        )

    def process_pdf(self, pdf_path: pathlib.Path):
        with httpx.Client(verify=False, follow_redirects=False) as httpx_client:
            pre_signed_uri = self._get_pre_signed_uri(httpx_client=httpx_client)
            self._put_file(
                httpx_client=httpx_client,
                pre_signed_uri=pre_signed_uri,
                pdf_path=pdf_path,
            )
            job_status_url = self._create_job(
                httpx_client=httpx_client, pre_signed_uri=pre_signed_uri
            )

            job_status = self._check_job_status(
                httpx_client=httpx_client, job_status_url=job_status_url
            )

            while job_status.is_progress():
                job_status = self._check_job_status(
                    httpx_client=httpx_client, job_status_url=job_status_url
                )
                sleep(2)

            if job_status.is_failed():
                raise AdobePDFServiceJobException("Job failed")
            elif job_status.is_done():
                return self._download_job_assets(
                    httpx_client=httpx_client,
                    download_uri=str(job_status.content.downloadUri),
                )
            else:
                raise AdobePDFServiceJobException("Unknown job status")

    def _get_pre_signed_uri(self, httpx_client: httpx.Client) -> PreSignedURI:
        logger.debug("[ADOBE-PDF-SERVICE] Getting pre-signed URI")
        res = httpx_client.post(
            url="https://pdf-services.adobe.io/assets",
            headers={
                "X-API-Key": self._client_id,
                "Authorization": f"Bearer {self._token.token}",
                "Content-Type": "application/json",
            },
            json={"mediaType": "application/pdf"},
        )

        return PreSignedURI(**res.json())

    def _put_file(
        self,
        httpx_client: httpx.Client,
        pre_signed_uri: PreSignedURI,
        pdf_path: pathlib.Path,
    ):
        logger.debug("[ADOBE-PDF_SERVICE] Uploading the file")
        res = httpx_client.put(
            url=str(pre_signed_uri.uploadUri),
            headers={
                "Content-Type": "application/pdf",
                # 'X-API-Key': self._client_id,
                # 'Authorization': f'Bearer {self._token.token}',
            },
            files={"upload-file": open(str(pdf_path.absolute()), "rb")},
        )

        if res.status_code != 200:
            raise AdobePDFServiceException(f"Uploading the file failed with status code {res.status_code}")

    def _create_job(self, httpx_client: httpx.Client, pre_signed_uri: PreSignedURI):
        logger.debug("[ADOBE-PDF_SERVICE] Creating job")
        res = httpx_client.post(
            url="https://pdf-services.adobe.io/operation/extractpdf",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self._client_id,
                "Authorization": f"Bearer {self._token.token}",
            },
            json={"assetID": pre_signed_uri.assetID},
        )

        location = res.headers.get("location", None)
        if location is None:
            raise AdobePDFServiceException("Location header is missing in the response from job creation")

        return location

    def _check_job_status(
        self, httpx_client: httpx.Client, job_status_url: str
    ) -> JobStatus:
        res = httpx_client.get(
            url=job_status_url,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self._client_id,
                "Authorization": f"Bearer {self._token.token}",
            },
        )

        job_status = JobStatus(**res.json())
        logger.debug(f"[ADOBE-PDF_SERVICE] Got job status: {job_status.status}")

        return

    def _download_job_assets(self, httpx_client: httpx.Client, download_uri: str) -> JobResult:
        logger.debug("[ADOBE-PDF_SERVICE] Downloading job assets")
        res = httpx_client.get(url=download_uri)
        return JobResult(**res.json())
