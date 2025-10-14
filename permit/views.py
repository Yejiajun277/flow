import json
from datetime import datetime
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import SyPermitBasic, SyPermitSafety


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def api_response(code=0, msg="ok", data=None):
    response_data = {
        "code": code,
        "msg": msg,
    }
    if data is not None:
        response_data["data"] = data
    return JsonResponse(response_data, encoder=CustomJSONEncoder)


@method_decorator(csrf_exempt, name='dispatch')
class PermitView(View):
    def get(self, request: HttpRequest, *args, **kwargs):  # 许可证列表（GET /permits）
        filters = Q()
        work_order_no = request.GET.get('work_order_no')
        if work_order_no:
            filters &= Q(work_order_no__icontains=work_order_no)
        permit_no = request.GET.get('permit_no')
        if permit_no:
            filters &= Q(permit_no__icontains=permit_no)
        facility_name = request.GET.get('facility_name')
        if facility_name:
            filters &= Q(facility_name__icontains=facility_name)
        application_date = request.GET.get('application_date')
        if application_date:
            try:
                valid_date = datetime.strptime(application_date, '%Y-%m-%d').date()
                filters &= Q(application_date=valid_date)
            except ValueError:
                return api_response(code=40001, msg="日期参数格式错误")
        queryset = SyPermitBasic.objects.filter(filters).order_by('permit_id')
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            if page > 100:
                page = 100
            if page < 1 or page_size < 1:
                return api_response(code=40001, msg="分页参数格式错误")
        except (TypeError, ValueError):
            return api_response(code=40001, msg="分页参数格式错误")
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = []
        data_list = [model_to_dict(item) for item in page_obj]
        response_data = {
            "list": data_list,
            "total": paginator.count,
            "page": page,
            "page_size": page_size
        }
        return api_response(data=response_data)

    def post(self, request: HttpRequest, *args, **kwargs):  # 创建许可证（POST /permits）
        try:
            data = json.loads(request.body)
            required_fields = [
                'facility_name', 'work_order_no', 'permit_no', 'scheme',
                'technical_disclosure', 'jsa', 'work_description', 'start_hour',
                'start_min', 'end_hour', 'end_min', 'work_location', 'equipment',
                'tools', 'hydraulic_pressure', 'airtight_operation',
                'operation_pressure', 'design_pressure', 'test_pressure',
                'supervisor', 'workers', 'guardian', 'applicant_unit',
                'applicant_name', 'application_date'
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return api_response(code=40001, msg=f"参数缺失: {', '.join(missing_fields)}")
            permit = SyPermitBasic.objects.create(**data)
            return api_response(data={"permit_id": permit.permit_id})
        except json.JSONDecodeError:
            return api_response(code=40001, msg="JSON 解析错误")
        except Exception as e:
            return api_response(code=500, msg=f"服务器内部错误: {e}")


class PermitDetailView(View):
    def get(self, request: HttpRequest, permit_id: int, *args, **kwargs):  # 获取许可证详情（GET /permits/{permit_id}）
        try:
            permit = SyPermitBasic.objects.get(pk=permit_id)
            permit_data = model_to_dict(permit)
            return api_response(data=permit_data)
        except SyPermitBasic.DoesNotExist:
            return api_response(code=40401, msg="指定的许可证不存在")


@method_decorator(csrf_exempt, name='dispatch')
class PermitSafetyView(View):
    def get(self, request: HttpRequest, permit_id: int, *args, **kwargs):  # 获取安全要求（GET /permits/{permit_id}/safety）
        try:
            safety_record = SyPermitSafety.objects.get(pk=permit_id)
            safety_data = model_to_dict(safety_record)
            return api_response(data=safety_data)
        except SyPermitSafety.DoesNotExist:
            return api_response(code=40401, msg="指定的许可证不存在对应的安全要求记录")

    def post(self, request: HttpRequest, permit_id: int, *args, **kwargs):  # 创建安全要求（POST /permits/{permit_id}/safety）
        try:
            SyPermitBasic.objects.get(pk=permit_id)
        except SyPermitBasic.DoesNotExist:
            return api_response(code=40401, msg="指定的许可证不存在")
        if SyPermitSafety.objects.filter(pk=permit_id).exists():
            return api_response(code=40901, msg="该许可证的安全要求记录已存在（请使用 PUT 更新）")
        try:
            data = json.loads(request.body)
            required_fields = [
                'ear_protection', 'goggles', 'gloves',
                'breathing_apparatus', 'safety_belt', 'life_jacket', 'walkie_talkie',
                'guard_ship', 'depressurization', 'pipeline_cleaning',
                'wind_direction_check', 'hole_blocking', 'overhead_line_check',
                'lighting_ok', 'coordination', 'scaffold_ladder', 'warning_sign',
                'first_aid', 'drain_block', 'tools_ok', 'guardian', 'other_1',
                'oxygen', 'flammable_gas', 'toxic_gas', 'electricity',
                'process_pneumatic_heat_source', 'mechanical_energy', 'signal_bypass',
                'temporarily_cancel'
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return api_response(code=40001, msg=f"参数缺失: {', '.join(missing_fields)}")
            data['permit_id'] = permit_id
            safety_record = SyPermitSafety.objects.create(**data)
            return api_response(data={"permit_id": safety_record.permit_id})
        except json.JSONDecodeError:
            return api_response(code=40001, msg="JSON 解析错误")
        except Exception as e:
            return api_response(code=500, msg=f"服务器内部错误: {e}")
