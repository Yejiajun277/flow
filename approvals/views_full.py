# approvals/views_full.py
from typing import Set
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from approvals.models import (
    PermitBasic, CentralReview, CentralManage, CentralSafety, CentralDirector,
    WellheadReview, WellheadDirector
)
from permit.models import SyPermitBasic, SyPermitSafety

from .serializers_full import (
    PermitBasicSerializer, PermitSafetySerializer,
    CentralReviewItemSerializer, CentralManageItemSerializer,
    CentralSafetyItemSerializer, CentralDirectorItemSerializer,
    WellheadReviewItemSerializer, WellheadDirectorItemSerializer
)

def api_response(code=0, msg="ok", data=None, http_status=status.HTTP_200_OK):
    return Response({"code": code, "msg": msg, "data": data}, status=http_status)

class PermitFullDetailView(APIView):
    """
    GET /api/v1.0/permits/{permit_id}/full
    可选参数: ?include=basic,safety,central,wellhead,status
    （不传 include 表示全部返回）
    """

    def get(self, request, permit_id: int):
        # 解析 include
        include_raw = request.query_params.get('include')
        if include_raw:
            include: Set[str] = {x.strip() for x in include_raw.split(',') if x.strip()}
        else:
            include = {"basic", "safety", "central", "wellhead", "status"}

        # 1) 基础信息存在性校验（两边模型互指同一张表）
        if not PermitBasic.objects.filter(pk=permit_id).exists():
            return api_response(40401, "指定的许可证不存在", http_status=status.HTTP_404_NOT_FOUND)

        data = {}

        # 2) basic_info
        if "basic" in include:
            try:
                basic = SyPermitBasic.objects.get(pk=permit_id)
            except SyPermitBasic.DoesNotExist:
                return api_response(40401, "指定的许可证不存在", http_status=status.HTTP_404_NOT_FOUND)
            data["basic_info"] = PermitBasicSerializer(basic).data

        # 3) safety_info（可能不存在，要求返回 null）
        if "safety" in include:
            safety = SyPermitSafety.objects.filter(pk=permit_id).first()
            data["safety_info"] = PermitSafetySerializer(safety).data if safety else None

        # 4) approvals（central / wellhead，按时间升序）
        if "central" in include or "wellhead" in include:
            approvals = {}

            if "central" in include:
                central_list = []
                review = CentralReview.objects.filter(permit_id=permit_id).first()
                if review:
                    central_list.append(CentralReviewItemSerializer(review).data)
                manage = CentralManage.objects.filter(permit_id=permit_id).first()
                if manage:
                    central_list.append(CentralManageItemSerializer(manage).data)
                safety = CentralSafety.objects.filter(permit_id=permit_id).first()
                if safety:
                    central_list.append(CentralSafetyItemSerializer(safety).data)
                director = CentralDirector.objects.filter(permit_id=permit_id).first()
                if director:
                    central_list.append(CentralDirectorItemSerializer(director).data)
                # 时间升序
                central_list.sort(key=lambda x: x['approval_date'])
                approvals["central"] = central_list

            if "wellhead" in include:
                wellhead_list = []
                w_review = WellheadReview.objects.filter(permit_id=permit_id).first()
                if w_review:
                    wellhead_list.append(WellheadReviewItemSerializer(w_review).data)
                w_director = WellheadDirector.objects.filter(permit_id=permit_id).first()
                if w_director:
                    wellhead_list.append(WellheadDirectorItemSerializer(w_director).data)
                wellhead_list.sort(key=lambda x: x['approval_date'])
                approvals["wellhead"] = wellhead_list

            if approvals:
                data["approvals"] = approvals

        # 5) status（是否存在记录的布尔聚合）
        if "status" in include:
            central_status = {
                "central_review":   CentralReview.objects.filter(permit_id=permit_id).exists(),
                "central_manage":   CentralManage.objects.filter(permit_id=permit_id).exists(),
                "central_safety":   CentralSafety.objects.filter(permit_id=permit_id).exists(),
                "central_director": CentralDirector.objects.filter(permit_id=permit_id).exists(),
            }
            wellhead_status = {
                "wellhead_review":   WellheadReview.objects.filter(permit_id=permit_id).exists(),
                "wellhead_director": WellheadDirector.objects.filter(permit_id=permit_id).exists(),
            }
            data["status"] = {"central": central_status, "wellhead": wellhead_status}

        return api_response(0, "ok", data)
    
from typing import Set, List, Dict
from collections import defaultdict

class PermitFullListView(APIView):
    """
    GET /api/v1.0/permits/full
    可选参数:
      - page, page_size
      - include=basic,safety,central,wellhead,status  (默认全部)
      - ids=1,2,3  (可选，若提供则只返回这些ID，仍支持分页)
    返回:
    {
      "code": 0,
      "msg": "ok",
      "data": {
        "list": [ { 单个permit的full结构 }, ... ],
        "total": <int>,
        "page": <int>,
        "page_size": <int>
      }
    }
    """

    def get(self, request):
        # include 解析
        include_raw = request.query_params.get('include')
        if include_raw:
            include: Set[str] = {x.strip() for x in include_raw.split(',') if x.strip()}
        else:
            include = {"basic", "safety", "central", "wellhead", "status"}

        # ids 解析（可选）
        ids_raw = request.query_params.get('ids')
        if ids_raw:
            try:
                selected_ids = [int(x) for x in ids_raw.split(',') if x.strip()]
            except ValueError:
                return api_response(40001, "ids 参数格式错误，应为逗号分隔的整数", http_status=status.HTTP_400_BAD_REQUEST)
        else:
            selected_ids = None

        # 分页参数
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
        except ValueError:
            return api_response(40002, "分页参数错误", http_status=status.HTTP_400_BAD_REQUEST)
        page = max(page, 1)
        page_size = max(min(page_size, 1000), 1)  # 防止一次拉太多

        # 先确定要处理的 PermitBasic ID 列表
        base_qs = PermitBasic.objects.all().order_by('pk')
        if selected_ids is not None:
            base_qs = base_qs.filter(pk__in=selected_ids)

        total = base_qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        ids_page: List[int] = list(base_qs.values_list('pk', flat=True)[start:end])

        if not ids_page:
            return api_response(0, "ok", {
                "list": [],
                "total": total,
                "page": page,
                "page_size": page_size
            })

        result_list: List[Dict] = []

        # ===== 批量查询并构建映射，避免 N+1 =====

        # basic
        basics_map: Dict[int, dict] = {}
        if "basic" in include:
            basics = SyPermitBasic.objects.filter(pk__in=ids_page)
            for b in basics:
                basics_map[b.pk] = PermitBasicSerializer(b).data

        # safety
        safety_map: Dict[int, dict] = {}
        if "safety" in include:
            safeties = SyPermitSafety.objects.filter(pk__in=ids_page)
            for s in safeties:
                safety_map[s.pk] = PermitSafetySerializer(s).data

        # approvals（central / wellhead）
        central_map: Dict[int, List[dict]] = defaultdict(list)
        wellhead_map: Dict[int, List[dict]] = defaultdict(list)

        if "central" in include:
            r_qs = CentralReview.objects.filter(permit_id__in=ids_page)
            m_qs = CentralManage.objects.filter(permit_id__in=ids_page)
            s_qs = CentralSafety.objects.filter(permit_id__in=ids_page)
            d_qs = CentralDirector.objects.filter(permit_id__in=ids_page)

            for obj in r_qs:
                central_map[obj.permit_id].append(CentralReviewItemSerializer(obj).data)
            for obj in m_qs:
                central_map[obj.permit_id].append(CentralManageItemSerializer(obj).data)
            for obj in s_qs:
                central_map[obj.permit_id].append(CentralSafetyItemSerializer(obj).data)
            for obj in d_qs:
                central_map[obj.permit_id].append(CentralDirectorItemSerializer(obj).data)

            # 每个 permit 的 central 流程按时间升序
            for pid in central_map:
                central_map[pid].sort(key=lambda x: x.get('approval_date'))

        if "wellhead" in include:
            wr_qs = WellheadReview.objects.filter(permit_id__in=ids_page)
            wd_qs = WellheadDirector.objects.filter(permit_id__in=ids_page)

            for obj in wr_qs:
                wellhead_map[obj.permit_id].append(WellheadReviewItemSerializer(obj).data)
            for obj in wd_qs:
                wellhead_map[obj.permit_id].append(WellheadDirectorItemSerializer(obj).data)

            for pid in wellhead_map:
                wellhead_map[pid].sort(key=lambda x: x.get('approval_date'))

        # status 聚合（存在性）
        status_map: Dict[int, Dict] = {}
        if "status" in include:
            cr_ids = set(CentralReview.objects.filter(permit_id__in=ids_page).values_list('permit_id', flat=True))
            cm_ids = set(CentralManage.objects.filter(permit_id__in=ids_page).values_list('permit_id', flat=True))
            cs_ids = set(CentralSafety.objects.filter(permit_id__in=ids_page).values_list('permit_id', flat=True))
            cd_ids = set(CentralDirector.objects.filter(permit_id__in=ids_page).values_list('permit_id', flat=True))
            wr_ids = set(WellheadReview.objects.filter(permit_id__in=ids_page).values_list('permit_id', flat=True))
            wd_ids = set(WellheadDirector.objects.filter(permit_id__in=ids_page).values_list('permit_id', flat=True))

            for pid in ids_page:
                central_status = {
                    "central_review":   pid in cr_ids,
                    "central_manage":   pid in cm_ids,
                    "central_safety":   pid in cs_ids,
                    "central_director": pid in cd_ids,
                }
                wellhead_status = {
                    "wellhead_review":   pid in wr_ids,
                    "wellhead_director": pid in wd_ids,
                }
                status_map[pid] = {"central": central_status, "wellhead": wellhead_status}

        # 组装每个 permit 的 full 结构
        for pid in ids_page:
            item = {"permit_id": pid}

            if "basic" in include:
                # 若不存在 basic，则与 detail 保持一致：返回 404？这里列表语义更友好：置为 None
                item["basic_info"] = basics_map.get(pid)

            if "safety" in include:
                item["safety_info"] = safety_map.get(pid)  # 可能为 None

            if "central" in include or "wellhead" in include:
                approvals = {}
                if "central" in include:
                    approvals["central"] = central_map.get(pid, [])
                if "wellhead" in include:
                    approvals["wellhead"] = wellhead_map.get(pid, [])
                item["approvals"] = approvals

            if "status" in include:
                item["status"] = status_map.get(pid, {
                    "central": {
                        "central_review": False,
                        "central_manage": False,
                        "central_safety": False,
                        "central_director": False,
                    },
                    "wellhead": {
                        "wellhead_review": False,
                        "wellhead_director": False,
                    }
                })

            result_list.append(item)

        return api_response(0, "ok", {
            "list": result_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
