# approvals/serializers.py
from rest_framework import serializers
from .models import (
    CentralReview, CentralManage, CentralSafety, CentralDirector,
    WellheadReview, WellheadDirector
)


class CentralReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralReview
        fields = ['assignment_supervisor', 'approval_date']


class CentralManageSerializer(serializers.ModelSerializer):
    # 1. 显式定义 approval_date 字段
    approval_date = serializers.DateTimeField(
        # 2. 强制指定只接受 'iso-8601' 格式的输入
        input_formats=['iso-8601']
    )

    class Meta:
        model = CentralManage
        fields = ['manage_supervision', 'approval_date']


class CentralSafetySerializer(serializers.ModelSerializer):
    # 将接口的 'safety_supervisor' 字段映射到模型的 'safety_supervision' 字段
    safety_supervisor = serializers.CharField(max_length=50, source='safety_supervision')

    class Meta:
        model = CentralSafety
        fields = ['safety_supervisor', 'approval_date']


class CentralDirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralDirector
        fields = ['chief_inspector', 'approval_date']


class WellheadReviewSerializer(serializers.ModelSerializer):
    # 显式定义 approval_date 字段，并强制其输入格式为 iso-8601
    approval_date = serializers.DateTimeField(
        input_formats=['iso-8601']
    )
    class Meta:
        model = WellheadReview
        fields = ['assignment_supervisor', 'approval_date']


class WellheadDirectorSerializer(serializers.ModelSerializer):
    # 显式定义 approval_date 字段，并强制其输入格式为 iso-8601
    approval_date = serializers.DateTimeField(
        input_formats=['iso-8601']
    )
    class Meta:
        model = WellheadDirector
        fields = ['chief_inspector', 'approval_date']
