# approvals/urls.py
from django.urls import path
from . import views, views_full


urlpatterns = [
    # 1.1 中心平台审批 (POST)
    path('permits/<int:permit_id>/approvals/central/review', views.CentralReviewCreateView.as_view(), name='central-review-create'),
    path('permits/<int:permit_id>/approvals/central/manage', views.CentralManageCreateView.as_view(), name='central-manage-create'),
    path('permits/<int:permit_id>/approvals/central/safety', views.CentralSafetyCreateView.as_view(), name='central-safety-create'),
    path('permits/<int:permit_id>/approvals/central/director', views.CentralDirectorCreateView.as_view(), name='central-director-create'),

    # 1.2 井口平台审批 (POST)
    path('permits/<int:permit_id>/approvals/wellhead/review', views.WellheadReviewCreateView.as_view(), name='wellhead-review-create'),
    path('permits/<int:permit_id>/approvals/wellhead/director', views.WellheadDirectorCreateView.as_view(), name='wellhead-director-create'),

    # 1.3 通用查询 (GET)
    path('permits/<int:permit_id>/approvals/central', views.CentralApprovalHistoryView.as_view(), name='central-history'),
    path('permits/<int:permit_id>/status/central', views.CentralApprovalStatusView.as_view(), name='central-status'),
    path('permits/<int:permit_id>/approvals/wellhead', views.WellheadApprovalHistoryView.as_view(), name='wellhead-history'),
    path('permits/<int:permit_id>/status/wellhead', views.WellheadApprovalStatusView.as_view(), name='wellhead-status'),

    # 全量查询 (GET)
    path('permits/<int:permit_id>/full', views_full.PermitFullDetailView.as_view()),
    path('permits/full', views_full.PermitFullListView.as_view())
]
