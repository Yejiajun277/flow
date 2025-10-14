from django.db import models

# Create your models here.
# approvals/models.py
from django.db import models

class PermitBasic(models.Model):
    # 这是主许可证表，审批记录将与它关联
    permit_id = models.BigAutoField(primary_key=True)
    # ... 此处省略其他字段，因为我们只需要外键关联 ...

    class Meta:
        managed = False  # Django 不管理此表
        db_table = 'sy_permit_basic'
        verbose_name = '许可证基础信息'

# --- 中心平台审批模型 ---

class CentralReview(models.Model):
    permit = models.OneToOneField(PermitBasic, on_delete=models.CASCADE, primary_key=True, db_column='permit_id')
    assignment_supervisor = models.CharField(max_length=50)
    approval_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sy_approval_central_review'
        verbose_name = '中心平台-审查'

class CentralManage(models.Model):
    permit = models.OneToOneField(PermitBasic, on_delete=models.CASCADE, primary_key=True, db_column='permit_id')
    manage_supervision = models.CharField(max_length=50)
    approval_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sy_approval_central_manage'
        verbose_name = '中心平台-主管审核'

class CentralSafety(models.Model):
    permit = models.OneToOneField(PermitBasic, on_delete=models.CASCADE, primary_key=True, db_column='permit_id')
    safety_supervision = models.CharField(max_length=50) # 注意：数据库字段名为 supervision
    approval_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sy_approval_central_safety'
        verbose_name = '中心平台-安全审核'

class CentralDirector(models.Model):
    permit = models.OneToOneField(PermitBasic, on_delete=models.CASCADE, primary_key=True, db_column='permit_id')
    chief_inspector = models.CharField(max_length=50)
    approval_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sy_approval_central_director'
        verbose_name = '中心平台-总监批准'

# --- 井口平台审批模型 ---

class WellheadReview(models.Model):
    permit = models.OneToOneField(PermitBasic, on_delete=models.CASCADE, primary_key=True, db_column='permit_id')
    assignment_supervisor = models.CharField(max_length=50)
    approval_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sy_approval_wellhead_review'
        verbose_name = '井口平台-审查'

class WellheadDirector(models.Model):
    permit = models.OneToOneField(PermitBasic, on_delete=models.CASCADE, primary_key=True, db_column='permit_id')
    chief_inspector = models.CharField(max_length=50)
    approval_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sy_approval_wellhead_director'
        verbose_name = '井口平台-批准'

