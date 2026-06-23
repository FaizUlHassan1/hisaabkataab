from django.urls import path

from bridge.views import (
    FBRProxyView,
    FBRHSUOMReferenceView,
    FBRItemCodesReferenceView,
    FBRUOMReferenceView,
    GetInvoiceDetailsView,
    HealthCheckView,
    PostInvoiceViewProduction,
    PostInvoiceViewSandbox,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("v1/fbr/proxy/", FBRProxyView.as_view(), name="fbr-proxy"),
    path(
        "v1/fbr/reference/item-codes/",
        FBRItemCodesReferenceView.as_view(),
        name="fbr-reference-item-codes",
    ),
    path(
        "v1/fbr/reference/uoms/",
        FBRUOMReferenceView.as_view(),
        name="fbr-reference-uoms",
    ),
    path(
        "v1/fbr/reference/hs-uom/",
        FBRHSUOMReferenceView.as_view(),
        name="fbr-reference-hs-uom",
    ),
    path("v1/fbr/invoices/", PostInvoiceViewProduction.as_view(), name="fbr-post-invoice"),
    path("v1/fbr/invoices_production/", PostInvoiceViewProduction.as_view(), name="fbr-post-invoice"),
    path("v1/fbr/invoices_sandbox", PostInvoiceViewSandbox.as_view(), name="fbr-post-invoice-sb"),
    path(
        "v1/fbr/invoices/details/",
        GetInvoiceDetailsView.as_view(),
        name="fbr-get-invoice-details",
    ),
]
