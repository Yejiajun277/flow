from django.urls import path

from permit import views

urlpatterns = [
    path('permits', views.PermitView.as_view(), name='permit-list'),
    path('permits/<int:permit_id>', views.PermitDetailView.as_view(), name='permit-detail'),
    path('permits/<int:permit_id>/safety', views.PermitSafetyView.as_view(), name='permit-safety'),
]