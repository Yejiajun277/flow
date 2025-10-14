from django.shortcuts import render

# Create your views here.
# approvals/views.py
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    PermitBasic, CentralReview, CentralManage, CentralSafety, CentralDirector,
    WellheadReview, WellheadDirector
)
from .serializers import (
    CentralReviewSerializer, CentralManageSerializer, CentralSafetySerializer, CentralDirectorSerializer,
    WellheadReviewSerializer, WellheadDirectorSerializer
)


# --- 辅助函数和基类 ---

def api_response(code, msg, data=None, status_code=status.HTTP_200_OK):
    """统一的 API 响应格式"""
    return Response({"code": code, "msg": msg, "data": data}, status=status_code)


class BaseApprovalCreateView(APIView):
    """处理审批记录创建的通用基类"""
    serializer_class = None
    model = None
    step_name = ""

    def post(self, request, permit_id):
        # 1. 检查许可证是否存在
        try:
            permit = PermitBasic.objects.get(pk=permit_id)
        except PermitBasic.DoesNotExist:
            return api_response(40401, "许可证不存在", status_code=status.HTTP_404_NOT_FOUND)

        # 2. 检查是否重复创建
        if self.model.objects.filter(permit=permit).exists():
            return api_response(40901, "该步骤审批已存在（重复创建）", status_code=status.HTTP_409_CONFLICT)

        # 3. 验证数据
        # views.py -> BaseApprovalCreateView -> post method

        # ... (前面的代码不变) ...

        # 3. 验证数据
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            # 检查是否为时间格式错误
            if 'approval_date' in serializer.errors:
                error_message = str(serializer.errors['approval_date'][0]).lower()  # 获取第一条错误信息并转为小写
                # 修改后的判断条件：检查是否包含 'format' 或 'invalid'，这比检查 'iso-8601' 更可靠
                if 'format' in error_message or 'invalid' in error_message:
                    return api_response(40002, "时间格式不合法（非 ISO-8601）",
                                        status_code=status.HTTP_400_BAD_REQUEST)

            # 如果不是特定的时间格式错误，则返回通用的参数错误
            return api_response(40001, "参数缺失或类型不符", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        # ... (后面的代码不变) ...


        # 4. 保存数据
        instance = serializer.save(permit=permit)

        # 5. 构建并返回成功响应
        response_data = serializer.data
        response_data['permit_id'] = permit_id
        response_data['step'] = self.step_name
        return api_response(0, "ok", response_data, status_code=status.HTTP_201_CREATED)


# --- 中心平台 POST 视图 ---

class CentralReviewCreateView(BaseApprovalCreateView):
    serializer_class = CentralReviewSerializer
    model = CentralReview
    step_name = "central_review"


class CentralManageCreateView(BaseApprovalCreateView):
    serializer_class = CentralManageSerializer
    model = CentralManage
    step_name = "central_manage"


class CentralSafetyCreateView(BaseApprovalCreateView):
    serializer_class = CentralSafetySerializer
    model = CentralSafety
    step_name = "central_safety"


class CentralDirectorCreateView(BaseApprovalCreateView):
    serializer_class = CentralDirectorSerializer
    model = CentralDirector
    step_name = "central_director"


# --- 井口平台 POST 视图 ---

class WellheadReviewCreateView(BaseApprovalCreateView):
    serializer_class = WellheadReviewSerializer
    model = WellheadReview
    step_name = "wellhead_review"


class WellheadDirectorCreateView(BaseApprovalCreateView):
    serializer_class = WellheadDirectorSerializer
    model = WellheadDirector
    step_name = "wellhead_director"


# --- 通用查询视图 ---

class CentralApprovalHistoryView(APIView):
    """GET: /permits/{permit_id}/approvals/central"""

    def get(self, request, permit_id):
        if not PermitBasic.objects.filter(pk=permit_id).exists():
            return api_response(40401, "许可证不存在", status_code=status.HTTP_404_NOT_FOUND)

        history = []
        # 查询并格式化每个步骤的数据
        review = CentralReview.objects.filter(permit_id=permit_id).first()
        if review:
            history.append({
                "step": "central_review",
                "assignment_supervisor": review.assignment_supervisor,
                "approval_date": review.approval_date
            })

        manage = CentralManage.objects.filter(permit_id=permit_id).first()
        if manage:
            history.append({
                "step": "central_manage",
                "manage_supervision": manage.manage_supervision,
                "approval_date": manage.approval_date
            })

        safety = CentralSafety.objects.filter(permit_id=permit_id).first()
        if safety:
            history.append({
                "step": "central_safety",
                "safety_supervisor": safety.safety_supervision,  # 返回接口文档定义的字段名
                "approval_date": safety.approval_date
            })

        director = CentralDirector.objects.filter(permit_id=permit_id).first()
        if director:
            history.append({
                "step": "central_director",
                "chief_inspector": director.chief_inspector,
                "approval_date": director.approval_date
            })

        # 按时间升序排序
        history.sort(key=lambda x: x['approval_date'])

        return api_response(0, "ok", history)


class CentralApprovalStatusView(APIView):
    """GET: /permits/{permit_id}/status/central"""

    def get(self, request, permit_id):
        if not PermitBasic.objects.filter(pk=permit_id).exists():
            return api_response(40401, "许可证不存在", status_code=status.HTTP_404_NOT_FOUND)

        data = {
            "central_review": CentralReview.objects.filter(permit_id=permit_id).exists(),
            "central_manage": CentralManage.objects.filter(permit_id=permit_id).exists(),
            "central_safety": CentralSafety.objects.filter(permit_id=permit_id).exists(),
            "central_director": CentralDirector.objects.filter(permit_id=permit_id).exists(),
        }
        return api_response(0, "ok", data)


class WellheadApprovalHistoryView(APIView):
    """GET: /permits/{permit_id}/approvals/wellhead"""

    def get(self, request, permit_id):
        if not PermitBasic.objects.filter(pk=permit_id).exists():
            return api_response(40401, "许可证不存在", status_code=status.HTTP_404_NOT_FOUND)

        history = []
        review = WellheadReview.objects.filter(permit_id=permit_id).first()
        if review:
            history.append({
                "step": "wellhead_review",
                "assignment_supervisor": review.assignment_supervisor,
                "approval_date": review.approval_date
            })

        director = WellheadDirector.objects.filter(permit_id=permit_id).first()
        if director:
            history.append({
                "step": "wellhead_director",
                "chief_inspector": director.chief_inspector,
                "approval_date": director.approval_date
            })

        history.sort(key=lambda x: x['approval_date'])
        return api_response(0, "ok", history)


class WellheadApprovalStatusView(APIView):
    """GET: /permits/{permit_id}/status/wellhead"""

    def get(self, request, permit_id):
        if not PermitBasic.objects.filter(pk=permit_id).exists():
            return api_response(40401, "许可证不存在", status_code=status.HTTP_404_NOT_FOUND)

        data = {
            "wellhead_review": WellheadReview.objects.filter(permit_id=permit_id).exists(),
            "wellhead_director": WellheadDirector.objects.filter(permit_id=permit_id).exists(),
        }
        return api_response(0, "ok", data)
