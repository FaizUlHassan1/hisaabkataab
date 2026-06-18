import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bridge.services.fbr_client import FBRClient, FBRClientError

logger = logging.getLogger(__name__)


def get_request_value(body, *keys):
    for key in keys:
        value = body.get(key)
        if value is not None:
            return value
    return None


def get_fbr_payload(body):
    payload = get_request_value(
        body,
        "fbr_request_body",
        "fbr_body",
        "fbr_payload",
        "data",
    )
    return body if payload is None else payload


def get_fbr_token(body):
    return get_request_value(
        body,
        "fbr_token",
        "fbr_authentication_token",
        "fbr_security_token",
        "fbrToken",
        "token",
        "auth_token",
        "authorization_token",
    )


def get_fbr_url(body):
    return get_request_value(
        body,
        "fbr_url",
        "fbr_server_url",
        "full_url",
    )


class HealthCheckView(APIView):
    """Public health check — no authentication required."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "fbr-bridge",
                "fbr_environment": settings.FBR_ENVIRONMENT,
            }
        )


class FBRProxyView(APIView):
    """
    Generic proxy endpoint for forwarding any FBR API call.

    POST /api/v1/fbr/proxy/

    Request body:
    {
        "method": "POST",                    // optional, default POST
        "data": { ... },                     // JSON payload for FBR
        "endpoint_name": "post_invoice",   // optional, uses known FBR paths
        "endpoint_path": "DigitalInvoicing/v1/PostInvoiceData_v1",  // optional override
        "full_url": "https://...",           // optional, bypass base URL
        "environment": "sandbox",            // optional: sandbox | sandbox_ssl | production
        "params": {},                        // optional query string params
        "headers": {}                        // optional extra headers
    }
    """

    def post(self, request):
        body = request.data

        if not isinstance(body, dict):
            return Response(
                {"error": "Request body must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = get_request_value(body, "data", "fbr_request_body", "fbr_body", "fbr_payload")
        if data is None:
            return Response(
                {"error": "Missing required field: data or fbr_request_body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fbr_token = get_fbr_token(body)
        client = FBRClient(
            environment=body.get("environment"),
            security_token=fbr_token,
        )

        try:
            result = client.forward_request(
                method=body.get("method", "POST"),
                data=data,
                endpoint_name=body.get("endpoint_name"),
                endpoint_path=body.get("endpoint_path"),
                full_url=body.get("full_url"),
                environment=body.get("environment"),
                extra_headers=body.get("headers"),
                params=body.get("params"),
                security_token=fbr_token,
            )
        except FBRClientError as exc:
            logger.warning("FBR client error: %s", exc)
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                    "status_code": exc.status_code,
                    "data": exc.response_body,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        http_status = (
            status.HTTP_200_OK
            if result["success"]
            else status.HTTP_502_BAD_GATEWAY
        )
        return Response(result, status=http_status)


class PostInvoiceViewProduction(APIView):
    """
    Convenience endpoint for posting invoice data to FBR.

    POST /api/v1/fbr/invoices/

    Request body: FBR invoice JSON (sent directly as the payload).
    Optional query param: ?environment=sandbox|sandbox_ssl|production
    """

    def post(self, request):
        body = request.data

        if not isinstance(body, dict):
            return Response(
                {"error": "Invoice data must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice_data = get_fbr_payload(body)
        environment = body.get("environment") or request.query_params.get("environment") or "production"
        fbr_token = get_fbr_token(body)
        fbr_url = get_fbr_url(body)
        endpoint_path = body.get("endpoint_path")
        client = FBRClient(environment=environment, security_token=fbr_token)
        print(client)
        try:
            result = client.forward_request(
                method="POST",
                data=invoice_data,
                endpoint_name="post_invoice",
                endpoint_path=endpoint_path,
                full_url=fbr_url,
                environment=environment,
                security_token=fbr_token,
            )
        except FBRClientError as exc:
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        http_status = (
            status.HTTP_200_OK
            if result["success"]
            else status.HTTP_502_BAD_GATEWAY
        )
        return Response(result, status=http_status)

class PostInvoiceViewSandbox(APIView):
    """
    Convenience endpoint for posting invoice data to FBR.

    POST /api/v1/fbr/invoices/

    Request body: FBR invoice JSON (sent directly as the payload).
    Optional query param: ?environment=sandbox|sandbox_ssl|production
    """

    def post(self, request):
        body = request.data

        if not isinstance(body, dict):
            return Response(
                {"error": "Invoice data must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice_data = get_fbr_payload(body)
        environment = body.get("environment") or request.query_params.get("environment") or "sandbox"
        fbr_token = get_fbr_token(body)
        fbr_url = get_fbr_url(body)
        endpoint_path = body.get("endpoint_path")
        client = FBRClient(environment=environment, security_token=fbr_token)

        try:
            result = client.forward_request(
                method="POST",
                data=invoice_data,
                endpoint_name="post_invoice",
                endpoint_path=endpoint_path,
                full_url=fbr_url,
                environment=environment,
                security_token=fbr_token,
            )
        except FBRClientError as exc:
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        http_status = (
            status.HTTP_200_OK
            if result["success"]
            else status.HTTP_502_BAD_GATEWAY
        )
        return Response(result, status=http_status)


class GetInvoiceDetailsView(APIView):
    """
    Convenience endpoint for fetching invoice details from FBR (sandbox).

    POST /api/v1/fbr/invoices/details/

    Request body: query parameters as JSON for FBR.
    """

    def post(self, request):
        query_data = request.data

        if not isinstance(query_data, dict):
            return Response(
                {"error": "Query data must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        environment = request.query_params.get("environment", "sandbox")
        client = FBRClient()

        try:
            result = client.forward_request(
                method="POST",
                data=query_data,
                endpoint_name="get_invoice_details",
                environment=environment,
            )
        except FBRClientError as exc:
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        http_status = (
            status.HTTP_200_OK
            if result["success"]
            else status.HTTP_502_BAD_GATEWAY
        )
        return Response(result, status=http_status)
