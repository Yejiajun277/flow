# approvals/serializers_full.py
from rest_framework import serializers
from permit.models import SyPermitBasic, SyPermitSafety  # 来自 permit 应用
from .models import (
    CentralReview, CentralManage, CentralSafety, CentralDirector,
    WellheadReview, WellheadDirector
)

# —— 基础信息/安全信息 ——（完全按表字段直出）
class PermitBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyPermitBasic
        fields = '__all__'   # 文档要求全字段返回

class PermitSafetySerializer(serializers.ModelSerializer):
    class Meta:
        model = SyPermitSafety
        fields = '__all__'   # 文档要求全字段返回

# —— 审批项（为统一输出键名，做轻量定制） ——
class CentralReviewItemSerializer(serializers.ModelSerializer):
    step = serializers.SerializerMethodField()
    class Meta:
        model = CentralReview
        fields = ['step', 'assignment_supervisor', 'approval_date']
    def get_step(self, obj): return 'central_review'

class CentralManageItemSerializer(serializers.ModelSerializer):
    step = serializers.SerializerMethodField()
    class Meta:
        model = CentralManage
        fields = ['step', 'manage_supervision', 'approval_date']
    def get_step(self, obj): return 'central_manage'

class CentralSafetyItemSerializer(serializers.ModelSerializer):
    # 对外字段名是 safety_supervisor，但模型字段叫 safety_supervision
    step = serializers.SerializerMethodField()
    safety_supervisor = serializers.CharField(source='safety_supervision')
    class Meta:
        model = CentralSafety
        fields = ['step', 'safety_supervisor', 'approval_date']
    def get_step(self, obj): return 'central_safety'

class CentralDirectorItemSerializer(serializers.ModelSerializer):
    step = serializers.SerializerMethodField()
    class Meta:
        model = CentralDirector
        fields = ['step', 'chief_inspector', 'approval_date']
    def get_step(self, obj): return 'central_director'

class WellheadReviewItemSerializer(serializers.ModelSerializer):
    step = serializers.SerializerMethodField()
    class Meta:
        model = WellheadReview
        fields = ['step', 'assignment_supervisor', 'approval_date']
    def get_step(self, obj): return 'wellhead_review'

class WellheadDirectorItemSerializer(serializers.ModelSerializer):
    step = serializers.SerializerMethodField()
    class Meta:
        model = WellheadDirector
        fields = ['step', 'chief_inspector', 'approval_date']
    def get_step(self, obj): return 'wellhead_director'
