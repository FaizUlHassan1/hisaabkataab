from django.urls import path

from bridge.views import (
    FBRProxyView,
    GetInvoiceDetailsView,
    HealthCheckView,
    PostInvoiceView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("v1/fbr/proxy/", FBRProxyView.as_view(), name="fbr-proxy"),
    path("v1/fbr/invoices/", PostInvoiceView.as_view(), name="fbr-post-invoice"),
    path(
        "v1/fbr/invoices/details/",
        GetInvoiceDetailsView.as_view(),
        name="fbr-get-invoice-details",
    ),
]
