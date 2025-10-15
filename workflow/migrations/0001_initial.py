"""Initial migration for workflow app."""

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Workflow",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("gmt_created", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("gmt_modified", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("name", models.CharField(max_length=50, verbose_name="名称")),
                ("description", models.CharField(max_length=50, verbose_name="描述")),
                (
                    "notices",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="CustomNotice中的id.逗号隔开多个通知方式",
                        max_length=50,
                        verbose_name="通知",
                    ),
                ),
                (
                    "view_permission_check",
                    models.BooleanField(
                        default=True,
                        help_text="开启后，只允许工单的关联人(创建人、曾经的处理人)有权限查看工单",
                        verbose_name="查看权限校验",
                    ),
                ),
                (
                    "limit_expression",
                    models.CharField(
                        blank=True,
                        default="{}",
                        help_text="限制周期({\"period\":24} 24小时), 限制次数({\"count\":1}在限制周期内只允许提交1次), 限制级别({\"level\":1} 针对(1单个用户 2全局)限制周期限制次数,默认特定用户);允许特定人员提交({\"allow_persons\":\"zhangsan,lisi\"}只允许张三提交工单,{\"allow_depts\":\"1,2\"}只允许部门id为1和2的用户提交工单，{\"allow_roles\":\"1,2\"}只允许角色id为1和2的用户提交工单)",
                        max_length=1000,
                        verbose_name="限制表达式",
                    ),
                ),
                (
                    "display_form_str",
                    models.CharField(
                        blank=True,
                        default="[]",
                        help_text="默认\"[]\"，用于用户只有对应工单查看权限时显示哪些字段,field_key的list的json,如[\"days\",\"sn\"],内置特殊字段participant_info.participant_name:当前处理人信息(部门名称、角色名称)，state.state_name:当前状态的状态名,workflow.workflow_name:工作流名称",
                        max_length=10000,
                        verbose_name="展现表单字段",
                    ),
                ),
                (
                    "title_template",
                    models.CharField(
                        blank=True,
                        default="你有一个待办工单:{title}",
                        help_text="工单字段的值可以作为参数写到模板中，格式如：你有一个待办工单:{title}",
                        max_length=50,
                        null=True,
                        verbose_name="标题模板",
                    ),
                ),
                (
                    "content_template",
                    models.CharField(
                        blank=True,
                        default="标题:{title}, 创建时间:{gmt_created}",
                        help_text="工单字段的值可以作为参数写到模板中，格式如：标题:{title}, 创建时间:{gmt_created}",
                        max_length=1000,
                        null=True,
                        verbose_name="内容模板",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="WorkflowAdmin",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("gmt_created", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("gmt_modified", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "username",
                    models.CharField(
                        help_text="除超级管理员及该工作流创建人外，管理人员也可以直接编辑该工作流",
                        max_length=100,
                        verbose_name="管理员",
                    ),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=models.deletion.DO_NOTHING,
                        to="workflow.workflow",
                        to_field="id",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Transition",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("gmt_created", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("gmt_modified", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("name", models.CharField(max_length=50, verbose_name="操作")),
                ("workflow_id", models.IntegerField(verbose_name="工作流id")),
                (
                    "transition_type_id",
                    models.IntegerField(
                        default=1,
                        help_text="1.常规流转，2.定时器流转,需要设置定时器时间",
                        verbose_name="流转类型",
                    ),
                ),
                (
                    "timer",
                    models.IntegerField(
                        default=0,
                        help_text="流转类型设置为定时器流转时生效,单位秒。处于源状态X秒后如果状态都没有过变化则自动流转到目标状态",
                        verbose_name="定时器(单位秒)",
                    ),
                ),
                ("source_state_id", models.IntegerField(verbose_name="源状态id")),
                ("destination_state_id", models.IntegerField(verbose_name="目的状态id")),
                (
                    "condition_expression",
                    models.CharField(
                        default="[]",
                        help_text="流转条件表达式，根据表达式中的条件来确定流转的下个状态，格式为[{\"expression\":\"{days} > 3 and {days}<10\", \"target_state_id\":11}] 其中{}用于填充工单的字段key,运算时会换算成实际的值，当符合条件下个状态将变为target_state_id中的值,表达式只支持简单的运算或datetime/time运算.loonflow会以首次匹配成功的条件为准，所以多个条件不要有冲突",
                        max_length=1000,
                        verbose_name="条件表达式",
                    ),
                ),
                (
                    "attribute_type_id",
                    models.IntegerField(
                        default=1,
                        help_text="属性类型，1.同意，2.拒绝，3.其他",
                        verbose_name="属性类型",
                    ),
                ),
                (
                    "field_require_check",
                    models.BooleanField(
                        default=True,
                        help_text="默认在用户点击操作的时候需要校验工单表单的必填项,如果设置为否则不检查。用于如\"退回\"属性的操作，不需要填写表单内容",
                        verbose_name="是否校验必填项",
                    ),
                ),
                ("alert_enable", models.BooleanField(default=False, verbose_name="点击弹窗提示")),
                ("alert_text", models.CharField(blank=True, default="", max_length=100, verbose_name="弹窗内容")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("gmt_created", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("gmt_modified", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("name", models.CharField(max_length=50, verbose_name="名称")),
                ("workflow_id", models.IntegerField(verbose_name="工作流")),
                (
                    "is_hidden",
                    models.BooleanField(
                        default=False,
                        help_text="设置为True时,获取工单步骤api中不显示此状态(当前处于此状态时除外)",
                        verbose_name="是否隐藏",
                    ),
                ),
                (
                    "order_id",
                    models.IntegerField(
                        default=0,
                        help_text="用于工单步骤接口时，step上状态的顺序(因为存在网状情况，所以需要人为设定顺序),值越小越靠前",
                        verbose_name="状态顺序",
                    ),
                ),
                (
                    "type_id",
                    models.IntegerField(
                        default=0,
                        help_text="0.普通类型 1.初始状态(用于新建工单时,获取对应的字段必填及transition信息) 2.结束状态(此状态下的工单不得再处理，即没有对应的transition)",
                        verbose_name="状态类型id",
                    ),
                ),
                (
                    "enable_retreat",
                    models.BooleanField(
                        default=False,
                        help_text="开启后允许工单创建人在此状态直接撤回工单到初始状态",
                        verbose_name="允许撤回",
                    ),
                ),
                (
                    "remember_last_man_enable",
                    models.BooleanField(
                        default=False,
                        help_text="开启后，到达此状态时会先检查之前是否有人在此状态处理过，如果有则处理人为最后一次处理的人",
                        verbose_name="记忆最后处理人",
                    ),
                ),
                (
                    "participant_type_id",
                    models.IntegerField(
                        blank=True,
                        default=1,
                        help_text="0.无处理人,1.个人,2.多人,3.部门,4.角色,5.变量(支持工单创建人,创建人的leader),6.脚本(已废弃),7.工单的字段内容(如表单中的\"测试负责人\"，需要为用户名或者逗号隔开的多个用户名),8.父工单的字段内容,10.hook,11.外部获取。 初始状态请选择类型5，参与人填creator",
                        verbose_name="参与者类型id",
                    ),
                ),
                (
                    "participant",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="可以为空(无处理人的情况，如结束状态)、username\\多个username(以,隔开)\\部门id\\角色id\\变量(creator,creator_tl)\\脚本记录的id等，包含子工作流的需要设置处理人为loonrobot",
                        max_length=1000,
                        verbose_name="参与者",
                    ),
                ),
                (
                    "distribute_type_id",
                    models.IntegerField(
                        default=1,
                        help_text="1.主动接单(如果当前处理人实际为多人的时候，需要先接单才能处理) 2.直接处理(即使当前处理人实际为多人，也可以直接处理) 3.随机分配(如果实际为多人，则系统会随机分配给其中一个人) 4.全部处理(要求所有参与人都要处理一遍,才能进入下一步)",
                        verbose_name="分配方式",
                    ),
                ),
                (
                    "state_field_str",
                    models.TextField(
                        default="{}",
                        help_text="json格式字典存储,包括读写属性1：只读，2：必填，3：可选. 示例：{\"created_at\":1,\"title\":2, \"sn\":1}, 内置特殊字段participant_info.participant_name:当前处理人信息(部门名称、角色名称)，state.state_name:当前状态的状态名,workflow.workflow_name:工作流名称",
                        verbose_name="表单字段",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        default="{}",
                        help_text="json格式，由调用方根据实际定制需求自行确定,如状态下需要显示哪些前端组件:{\"components\":[{\"AppList\":1, \"ProjectList\":7}]}",
                        max_length=1000,
                        verbose_name="状态标签",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

