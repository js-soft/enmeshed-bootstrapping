from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel

# As Host: Connector API
_CONNECTOR_BASE_URL = "http://localhost:3000"
_CONNECTOR_API_KEY = "This_is_a_test_APIKEY_with_30_chars+"


class GetHealthResponse(BaseModel):
    isHealthy: bool
    services: dict[str, str]


class PostOwnRLTResponse_result_reference(BaseModel):
    truncated: str
    url: str


class PostOwnRLTResponse_result(BaseModel):
    id: str
    isOwn: bool
    createdBy: str
    createdByDevice: str
    createdAt: datetime
    content: dict[str, Any]  # pyright: ignore[reportExplicitAny]
    expiresAt: datetime
    maxNumberOfAllocations: int
    reference: PostOwnRLTResponse_result_reference


class PostOwnRLTResponse(BaseModel):
    result: PostOwnRLTResponse_result


class GetRelationshipsResponse_result(BaseModel):
    id: str
    templateId: str
    status: str
    peer: str


class GetRelationshipsResponse(BaseModel):
    result: list[GetRelationshipsResponse_result]


class PostOwnFileResponse_result_reference(BaseModel):
    truncated: str
    url: str


class PostOwnFileResponse_result(BaseModel):
    id: str
    isOwn: bool
    filename: str
    filesize: int
    createdAt: datetime
    createdBy: str
    createdByDevice: str
    expiresAt: datetime
    mimetype: str
    title: str
    description: str
    owner: str
    ownershipToken: str
    reference: PostOwnFileResponse_result_reference


class PostOwnFileResponse(BaseModel):
    result: PostOwnFileResponse_result


class GetOwnFileResponse(BaseModel):
    pass


class ConnectorSDK:
    _http: httpx.Client

    def __init__(
        self,
        base_url: str = _CONNECTOR_BASE_URL,
        api_key: str = _CONNECTOR_API_KEY,
    ) -> None:

        self._http = httpx.Client(
            base_url=base_url,
            headers={"X-API-KEY": api_key},
        )

    def get_health(self) -> GetHealthResponse:
        path = "/health"
        resp = self._send("GET", path)
        _ = resp.raise_for_status()
        return GetHealthResponse.model_validate(resp.json())

    def post_own_rlt(
        self,
        content: dict[str, object],
        max_num_allocs: int,
        expires_at: datetime,
    ) -> PostOwnRLTResponse:
        path = "/api/core/v1/RelationshipTemplates/Own"
        json = {
            "maxNumberOfAllocations": max_num_allocs,
            "expiresAt": expires_at.isoformat(timespec="milliseconds"),
            "content": content,
        }
        resp = self._send("POST", path, json=json)  # pyright: ignore[reportArgumentType]
        _ = resp.raise_for_status()
        return PostOwnRLTResponse.model_validate(resp.json())

    def post_message(
        self,
        recipient_addr: str,
        title: str,
        body: str,
        attachments: list[str] | None = None,
    ) -> None:
        if attachments is None:
            attachments = []

        path = "/api/core/v1/Messages"
        data = {
            "recipients": [recipient_addr],
            "content": {
                "@type": "Mail",
                "to": [recipient_addr],
                "subject": title,
                "body": body,
                "bodyFormat": "PlainText",
            },
            "attachments": attachments,
        }
        resp = self._send("POST", path, json=data)  # pyright: ignore[reportArgumentType]
        _ = resp.raise_for_status()
        return None

    def get_relationships(
        self,
        peer: str,
        status: str,
    ) -> GetRelationshipsResponse:
        path = "/api/core/v1/Relationships"
        resp = self._send(
            "GET",
            path,
            params={
                "peer": peer,
                "status": status,
            },
        )
        _ = resp.raise_for_status()
        return GetRelationshipsResponse.model_validate(resp.json())

    def post_own_file(
        self,
        title: str,
        description: str,
        data: bytes,
        filename: str,
        mimetype: str,
    ) -> PostOwnFileResponse:
        path = "/api/core/v1/Files/Own"
        resp = self._send(
            "POST",
            path,
            data={"title": title, "description": description},
            files={"file": (filename, data, mimetype)},
        )
        _ = resp.raise_for_status()
        return PostOwnFileResponse.model_validate(resp.json())

    def _send(
        self,
        method: str,
        path: str,
        json: dict[object, object] | None = None,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> httpx.Response:
        return self._http.request(
            method, path, json=json, params=params, data=data, files=files
        )
