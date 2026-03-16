from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel


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


class ConnectorSDK:
    _http: httpx.Client

    def __init__(
        self,
        base_url: str,
        api_key: str,
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

    def post_own_rlt(self) -> PostOwnRLTResponse:
        path = "/api/core/v1/RelationshipTemplates/Own"
        json = {
            "maxNumberOfAllocations": 100,
            "expiresAt": "2029-01-01T00:00:00.000Z",
            "content": {
                "@type": "RelationshipTemplateContent",
                "title": "Huhu =)",
                "onNewRelationship": {
                    "@type": "Request",
                    "items": [
                        {
                            "@type": "ConsentRequestItem",
                            "consent": "...",
                            "requiresInteraction": False,
                            "mustBeAccepted": False,
                        }
                    ],
                },
            },
        }
        resp = self._send("POST", path, json=json)  # pyright: ignore[reportArgumentType]
        _ = resp.raise_for_status()
        return PostOwnRLTResponse.model_validate(resp.json())

    def post_message(
        self,
        recipient_addr: str,
        title: str,
        body: str,
    ) -> None:
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

    def _send(
        self,
        method: str,
        path: str,
        json: dict[object, object] | None = None,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self._http.request(method, path, json=json, params=params)
