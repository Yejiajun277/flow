# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you want to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models


class SyPermitBasic(models.Model):
    """
    作业许可基础信息模型
    """
    permit_id = models.BigAutoField(primary_key=True, help_text='许可证 ID (KEY)')
    facility_name = models.CharField(max_length=100, help_text='设备名称')
    work_order_no = models.CharField(max_length=50, help_text='工作单号')
    permit_no = models.CharField(max_length=50, help_text='许可证编号')
    scheme = models.BooleanField(help_text='许可可行性')
    technical_disclosure = models.BooleanField(help_text='施工方案要求')
    jsa = models.BooleanField(help_text='技术交底')
    work_description = models.TextField(help_text='工作内容，当前作业描述')
    start_hour = models.SmallIntegerField(help_text='作业开始时间（时。分钟制）')
    start_min = models.SmallIntegerField(help_text='作业开始时间（分钟）')
    end_hour = models.SmallIntegerField(help_text='作业结束时间（时。分钟制）')
    end_min = models.SmallIntegerField(help_text='作业结束时间（分钟）')
    work_location = models.CharField(max_length=200, help_text='作业所在位置')
    equipment = models.CharField(max_length=100, help_text='作业使用的设备')
    tools = models.CharField(max_length=100, help_text='作业所使用工具')
    hydraulic_pressure = models.BooleanField(help_text='水压')
    airtight_operation = models.BooleanField(help_text='操作气密性')
    operation_pressure = models.DecimalField(max_digits=10, decimal_places=2, help_text='操作压力 (Kpa)')
    design_pressure = models.DecimalField(max_digits=10, decimal_places=2, help_text='设计压力 (Kpa)')
    test_pressure = models.DecimalField(max_digits=10, decimal_places=2, help_text='测试压力 (Kpa)')
    supervisor = models.CharField(max_length=50, help_text='监督人')
    workers = models.TextField(help_text='作业人')
    guardian = models.CharField(max_length=50, help_text='监护人')
    applicant_unit = models.CharField(max_length=100, help_text='申请单位')
    applicant_name = models.CharField(max_length=50, help_text='申请人')
    application_date = models.DateField(help_text='申请日期')

    class Meta:
        managed = False
        db_table = 'sy_permit_basic'
        verbose_name = '作业许可基础信息'
        verbose_name_plural = verbose_name


class SyPermitSafety(models.Model):
    """
    作业许可安全措施模型
    """
    permit = models.OneToOneField(SyPermitBasic, on_delete=models.CASCADE, primary_key=True, help_text='许可证 ID')
    potential_hazards = models.TextField(blank=True, null=True, help_text='潜在危险')
    ear_protection = models.BooleanField(help_text='戴耳保护器')
    goggles = models.BooleanField(help_text='戴护目镜')
    gloves = models.BooleanField(help_text='戴手套')
    breathing_apparatus = models.BooleanField(help_text='戴呼吸器')
    safety_belt = models.BooleanField(help_text='佩戴安全带')
    life_jacket = models.BooleanField(help_text='佩戴救生衣')
    walkie_talkie = models.BooleanField(help_text='佩戴对讲机')
    guard_ship = models.BooleanField(help_text='警戒船只')
    depressurization = models.BooleanField(help_text='降压操作')
    pipeline_cleaning = models.BooleanField(help_text='管道清洗')
    wind_direction_check = models.BooleanField(help_text='风向检查')
    hole_blocking = models.BooleanField(help_text='孔洞封堵')
    overhead_line_check = models.BooleanField(help_text='周围是否有高压电线')
    lighting_ok = models.BooleanField(help_text='照明要求良好')
    coordination = models.BooleanField(help_text='协调好相关人员')
    scaffold_ladder = models.BooleanField(help_text='脚手架/梯子')
    warning_sign = models.BooleanField(help_text='警示标志')
    first_aid = models.BooleanField(help_text='急救设备')
    drain_block = models.BooleanField(help_text='排水设施')
    tools_ok = models.BooleanField(help_text='工具符合要求')
    guardian = models.BooleanField(help_text='监护人')
    other_1 = models.BooleanField(help_text='其他1')
    other_2 = models.CharField(max_length=50, blank=True, null=True, help_text='其他内容')
    oxygen = models.BooleanField(help_text='氧气')
    flammable_gas = models.BooleanField(help_text='易燃气体')
    toxic_gas = models.BooleanField(help_text='有毒气体')
    detection_num = models.IntegerField(blank=True, null=True, help_text='检测编号')
    isolation_notes1 = models.CharField(max_length=100, blank=True, null=True, help_text='隔离注释')
    gas_person = models.CharField(max_length=50, blank=True, null=True, help_text='气体人员')
    detector_model = models.CharField(max_length=50, blank=True, null=True, help_text='检测仪型号')
    electricity = models.BooleanField(help_text='电气')
    process_pneumatic_heat_source = models.BooleanField(help_text='工艺/气动/热源')
    mechanical_energy = models.BooleanField(help_text='机械能')
    signal_bypass = models.BooleanField(help_text='信号旁路')
    temporarily_cancel = models.BooleanField(help_text='暂时取消')
    isolation_notes2 = models.CharField(max_length=100, blank=True, null=True, help_text='隔离注释2')
    isolation_notes3 = models.CharField(max_length=100, blank=True, null=True, help_text='隔离注释3')
    emergency_plan = models.CharField(max_length=100, blank=True, null=True)
    related_permits = models.CharField(max_length=100, blank=True, null=True, help_text='相关许可证')

    class Meta:
        managed = False
        db_table = 'sy_permit_safety'
        verbose_name = '作业许可安全措施'
        verbose_name_plural = verbose_name
