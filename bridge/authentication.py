import logging

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class BridgeAPIKeyUser:
    """Lightweight user object for authenticated bridge requests."""

    is_authenticated = True


class BridgeAPIKeyAuthentication(BaseAuthentication):
    """
    Authenticate ERP requests using the X-API-Key header.
    """

    keyword = "X-API-Key"

    def authenticate(self, request):
        api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
        expected_key = settings.BRIDGE_API_KEY

        if not expected_key:
            logger.error("BRIDGE_API_KEY is not configured on the server")
            raise AuthenticationFailed("Bridge API key is not configured on the server.")

        if not api_key:
            raise AuthenticationFailed("Missing X-API-Key header.")

        if api_key != expected_key:
            raise AuthenticationFailed("Invalid API key.")

        return (BridgeAPIKeyUser(), api_key)
