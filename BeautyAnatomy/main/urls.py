from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (ProductDetailView,
                    CategoryDetailView,
                    CategoryView,
                    CartView,
                    AddToCartView,
                    DeleteFromCartView,
                    ChangeQTYView,
                    CheckoutView,
                    MakeOrderView
                    )

urlpatterns = [
    path('', views.index, name='main'),
    path('shop/', CategoryView.as_view(), name='shop'),
    path('products/<str:ct_model>/<str:slug>', ProductDetailView.as_view(), name='single-product'),
    path('category/<str:slug>', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-to-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty-from-to-cart/<str:ct_model>/<str:slug>/', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
