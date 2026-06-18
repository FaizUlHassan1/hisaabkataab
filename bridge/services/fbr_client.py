import logging
from typing import Any
from urllib.parse import urljoin

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class FBRClientError(Exception):
    def __init__(self, message: str, status_code: int | None = None, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class FBRClient:
    """HTTP client for forwarding requests to FBR Digital Invoicing APIs."""

    def __init__(self):
        self.environment = settings.FBR_ENVIRONMENT
        self.security_token = settings.FBR_SECURITY_TOKEN
        self.timeout = settings.FBR_REQUEST_TIMEOUT
        self.verify_ssl = settings.FBR_VERIFY_SSL

    def _get_base_url(self, environment: str | None = None) -> str:
        env = (environment or self.environment).lower()
        base_url = settings.FBR_BASE_URLS.get(env)
        if not base_url:
            raise FBRClientError(f"Unknown FBR environment: {env}")
        return base_url.rstrip("/") + "/"

    def _build_url(self, endpoint: str, environment: str | None = None) -> str:
        endpoint = endpoint.lstrip("/")
        return urljoin(self._get_base_url(environment), endpoint)

    def _resolve_endpoint(self, endpoint_name: str | None, endpoint_path: str | None) -> str:
        if endpoint_path:
            return endpoint_path

        if endpoint_name:
            resolved = settings.FBR_ENDPOINTS.get(endpoint_name)
            if not resolved:
                raise FBRClientError(
                    f"Unknown endpoint name '{endpoint_name}'. "
                    f"Known names: {', '.join(settings.FBR_ENDPOINTS.keys())}"
                )
            return resolved

        return settings.FBR_ENDPOINTS["post_invoice"]

    def _get_headers(self, extra_headers: dict | None = None) -> dict:
        if not self.security_token:
            raise FBRClientError("FBR_SECURITY_TOKEN is not configured on the bridge server.")

        headers = {
            "Authorization": f"Bearer {self.security_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def forward_request(
        self,
        *,
        method: str = "POST",
        data: dict | list | None = None,
        endpoint_name: str | None = None,
        endpoint_path: str | None = None,
        full_url: str | None = None,
        environment: str | None = None,
        extra_headers: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """
        Forward a request to FBR and return a structured response.

        Returns:
            {
                "success": bool,
                "status_code": int,
                "data": parsed JSON or raw text,
                "fbr_url": str,
            }
        """
        method = method.upper()
        url = full_url or self._build_url(
            self._resolve_endpoint(endpoint_name, endpoint_path),
            environment=environment,
        )

        logger.info("Forwarding %s request to FBR: %s", method, url)

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=self._get_headers(extra_headers),
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except requests.exceptions.SSLError as exc:
            logger.exception("SSL error connecting to FBR")
            raise FBRClientError(
                "SSL error connecting to FBR. "
                "If using sandbox, try FBR_VERIFY_SSL=False or FBR_ENVIRONMENT=sandbox_ssl.",
            ) from exc
        except requests.exceptions.Timeout as exc:
            logger.exception("FBR request timed out")
            raise FBRClientError("FBR request timed out.") from exc
        except requests.exceptions.ConnectionError as exc:
            logger.exception("Could not connect to FBR")
            raise FBRClientError("Could not connect to FBR server.") from exc
        except requests.exceptions.RequestException as exc:
            logger.exception("FBR request failed")
            raise FBRClientError(f"FBR request failed: {exc}") from exc

        response_data = self._parse_response_body(response)

        result = {
            "success": response.ok,
            "status_code": response.status_code,
            "data": response_data,
            "fbr_url": url,
        }

        logger.info("FBR responded with status %s", response.status_code)
        return result

    @staticmethod
    def _parse_response_body(response: requests.Response) -> Any:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError:
                return response.text
        return response.text
