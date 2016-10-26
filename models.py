#-*-coding:utf-8-*-
from openerp import fields,api
from openerp import models

class equipment_info(models.Model):
    _name ='asset_management.equipment_info'
    _rec_name = 'SN'

    SN = fields.Char(string=u"序列号",required=True)
    firms = fields.Char( string=u"设备厂商",required=True)
    device_type = fields.Char(string=u"设备类型",required=True)
    asset_number = fields.Char(string=u"资产编号",required=True)
    unit_type = fields.Char(string=u"设备型号",required=True)
    equipment_source = fields.Char(string=u"设备来源",required=True)
    equipment_status = fields.Selection([(u'库存', u"库存"),
                               (u'故障', u"故障"),
                               (u'专用', u"专用"),
                               (u'待报废', u"待报废"),
                               (u'暂存', u"暂存"),
                               ],string=u"设备状态",required=True)
    equipment_use = fields.Selection([
                               (u'公共备件', u"公共备件"),
                               (u'专用备件', u"专用备件"),
                               (u'故障件', u"故障件"),
                               (u'待报废', u"待报废"),
                               (u'暂存设备', u"暂存设备"),
                                ],string=u"设备用途",required=True)
    owner = fields.Char(string=u"归属人",required=True)
    company = fields.Boolean(string=u"公司资产",required=True)
    note = fields.Char(string=u"备注")
    floor = fields.Char(string=u"存放楼层")
    area = fields.Char(string=u"存放区域")
    seat = fields.Char(string=u"库存位置")
    machine_room = fields.Char(string=u"存放机房")
    cabinet_number = fields.Char(string=u"机柜编号")
    start_u_post = fields.Char(string=u"起始U位")
    storage_id = fields.Many2many('asset_management.equipment_storage',"storge_equipment_ref",)
    get_ids = fields.Many2many('asset_management.equipment_get',"get_equipment_ref",)
    lend_ids = fields.Many2many('asset_management.equipment_lend',"lend_equipment_ref",)
    apply_ids = fields.Many2many('asset_management.equipment_it_apply',"IT_equipment_ref" ,)

class equipment_storage(models.Model):
    _name = 'asset_management.equipment_storage'
    _rec_name = 'storage_id'

    storage_id = fields.Char(string=u"入库单号")
    user_id = fields.Many2one('res.users', string=u"申请人", required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人")
    # SN = fields.Char()
    SN = fields.Many2many('asset_management.equipment_info',"storge_equipment_ref",string=u"设备SN",required=True)
    state = fields.Selection([
        ('demander', u"需求方申请"),
        ('ass_admin', u"资产管理员"),
        ('ass_admin_manager', u"资产管理部门主管"),
        ('owner', u"资产归属人"),
    ],string=u"状态",required=True,default='demander')

class equipment_lend(models.Model):
    _name = 'asset_management.equipment_lend'
    _rec_name = 'lend_id'

    lend_id = fields.Char(string=u"借用单号")
    user_id = fields.Many2one('res.users', string=u"申请人", required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人")
    SN = fields.Many2many('asset_management.equipment_info',"lend_equipment_ref", string=u"设备SN", required=True)
    state = fields.Selection([
            ('demander', u"需求方申请"),
            ('ass_admin', u"资产管理员"),
            ('dem_leader', u"需求方直属部门领导"),
            ('dem_leader_manager', u"需求方直属主管"),# 副总裁级
            ('ass_director', u"资产管理部门负责人"),
            ('ass_admin_manager', u"资产管理部门主管"),  # 副总裁级MA
    ], string=u"状态", required=True,default='demander')
    lend_date = fields.Date(string=u"借用日期",required=True)
    promise_date = fields.Date(string=u"承诺归还日期",required=True)
    actual_date = fields.Date(string=u"实际归还日期",required=True)
    lend_purpose = fields.Char(string=u"借用目的",required=True)

class equipment_get(models.Model):
    _name = 'asset_management.equipment_get'
    _rec_name = 'get_id'

    def _default_SN(self):
        return self.env['asset_management.equipment_info'].browse(self._context.get('active_ids'))
    get_id = fields.Char(string=u"领用单号")
    user_id = fields.Many2one('res.users', string=u"申请人", required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人")
    SN = fields.Many2many('asset_management.equipment_info',"get_equipment_ref",string=u"设备SN", default=_default_SN,required=True)
    state = fields.Selection([
            ('demander', u"需求方申请"),
             ('ass_admin', u"资产管理员"),
             ('dem_leader', u"需求方直属部门领导"),
             ('ass_director', u"资产管理部门负责人"),
             ('ass_admin_manager', u"资产管理部门主管"),  # 副总裁级MA
    ], string=u"状态", required=True,default='demander')
    get_date = fields.Date(string=u"领用日期")
    get_purpose = fields.Char(string=u"领用目的",required=True)

    @api.multi
    def subscribe(self):
        return {'aaaaaaaaaaaaaa'}

class equipment_it_apply(models.Model):
    _name = 'asset_management.equipment_it_apply'
    _rec_name = 'apply_id'

    apply_id = fields.Char(string=u"申请IT环境单号")
    user_id = fields.Many2one('res.users', string=u"申请人", required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人")
    SN = fields.Many2many('asset_management.equipment_info',"IT_equipment_ref" ,string=u"设备SN", required=True)
    state = fields.Selection([

             ('demander', u"需求方申请"),
             ('ass_admin', u"资产管理员"),
             ('dem_leader', u"需求方直属部门领导"),
             ('dem_leader_manager', u"需求方直属主管"),# 副总裁级
             ('ass_director', u"资产管理部门负责人"),
             ('ass_admin_manager', u"资产管理部门主管"),  # 副总裁级MA
    ], string=u"状态", required=True,default='demander')
    use_begin = fields.Date(string=u"使用开始时间",required=True)
    use_over = fields.Date(string=u"使用结束时间",required=True)
    up_date = fields.Date(string=u"设备上架时间",required=True)
    down_date = fields.Date(string=u"设备下架时间",required=True)
    tester = fields.Many2one('res.users',string=u"测试人员",required=True)
    # 这个需要邮件提醒
    application_purpose = fields.Char(string=u"申请目的",required=True)

class entry_store_examine(models.Model):
    _name='asset_management.entry_store_examine'
    _rec_name = 'exam_num'
    exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users',required = 'True',string='审批人')
    date = fields.Date(string='审批时间')
    result=fields.Selection([
                               (u'通过', u"通过"),
                               (u'拒绝', u"拒绝"),

                                ],string=u"通过")
    store_id = fields.Many2one('asset_management.equipment_storage',string='入库单')
    reason = fields.Char(string='原因')

class lend_examine(models.Model):
    _name = 'asset_management.lend_examine'
    _rec_name = 'exam_num'

    exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users', required='True', string='审批人')
    date = fields.Date(string='审批时间')
    result = fields.Selection([
        (u'通过', u"通过"),
        (u'拒绝', u"拒绝"),

    ], string=u"通过")
    store_id = fields.Many2one('asset_management.equipment_lend', string='借用单')
    reason = fields.Char(string='原因')
class get_examine(models.Model):
    _name = 'asset_management.get_examine'
    _rec_name = 'exam_num'

    exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users', required='True', string='审批人')
    date = fields.Date(string='审批时间')
    result = fields.Selection([
        (u'通过', u"通过"),
        (u'拒绝', u"拒绝"),

    ], string=u"通过")
    store_id = fields.Many2one('asset_management.equipment_get', string='领用')
    reason = fields.Char(string='原因')

class IT_examine(models.Model):
    _name = 'asset_management.it_examine'
    _rec_name = 'exam_num'

    exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users', required='True', string='审批人')
    date = fields.Date(string='审批时间')
    result = fields.Selection([
        (u'通过', u"通过"),
        (u'拒绝', u"拒绝"),

    ], string=u"通过")
    store_id = fields.Many2one('asset_management.equipment_it_apply', string='IT环境申请单')
    reason = fields.Char(string='原因')
