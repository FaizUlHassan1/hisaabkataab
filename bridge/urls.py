from django.urls import path

from bridge.views import (
    FBRProxyView,
    GetInvoiceDetailsView,
    HealthCheckView,
    PostInvoiceViewProduction,
    PostInvoiceViewSandbox,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("v1/fbr/proxy/", FBRProxyView.as_view(), name="fbr-proxy"),
    path("v1/fbr/invoices/", PostInvoiceViewProduction.as_view(), name="fbr-post-invoice"),
    path("v1/fbr/invoices_production/", PostInvoiceViewProduction.as_view(), name="fbr-post-invoice"),
    path("v1/fbr/invoices_sandbox", PostInvoiceViewSandbox.as_view(), name="fbr-post-invoice-sb"),
    path(
        "v1/fbr/invoices/details/",
        GetInvoiceDetailsView.as_view(),
        name="fbr-get-invoice-details",
    ),
]
