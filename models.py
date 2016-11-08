#-*-coding:utf-8-*-
from openerp import fields,api
from openerp import models
from email.utils import formataddr
import email
from email.header import Header

class equipment_info(models.Model):
    _name ='asset_management.equipment_info'
    _rec_name = 'sn'

    sn = fields.Char(string=u"序列号",required=True)
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
    state = fields.Selection([
        (u'待入库',u'待入库'),
        (u'已入库',u'已入库'),
        (u'流程中',u'流程中'),
        (u'领用',u'领用'),
        (u'借用',u'借用'),
        (u'IT环境',u'IT环境'),
    ],string='状态',default=u'待入库')
    owner = fields.Many2one('res.users',string=u"归属人",required=True)
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


    _sql_constraints = [
        ('SN UNIQUE',
         'UNIQUE(sn)',
         '该序列号已存在'),
    ]

    def send_email(self, cr, uid, users, data=[], context=None):
        # template_model = self.pool.get('email.template')
        # ids = template_model.search(cr, uid, [('name', '=', 'case邮件提醒')], context=None)
        # template = template_model.browse(cr, uid, ids, context=None)
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name, 'utf-8').encode(), user.email)))
        mail_mail = self.pool.get('mail.mail')
        for i in range(len(data)):
            if not data[i]:
                data[i] = ''
        mail_id = mail_mail.create(cr, uid, {
            'body_html': '<div><p>您好:</p>'
                         '<p>这个case需要您处理,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a></p></div>',
            # 'subject': 'Re: %s+%s+%s' %(str(data[0]).decode('utf-8').encode('gbk'),str(data[1]).decode('utf-8').encode('gbk'),str(data[2]).decode('utf-8').encode('gbk')),
            'subject': data[0] + u',' + data[1] + u',' + data[2],
            'email_to': to_list,
            'auto_delete': True,
        }, context=context)
        mail_mail.send(cr, uid, [mail_id], context=context)


class equipment_storage(models.Model):
    _name = 'asset_management.equipment_storage'
    _rec_name = 'storage_id'

    @api.multi
    def _default_SN(self):
        return self.env['asset_management.equipment_info'].search([('state', '=', u'待入库')])

    storage_id = fields.Char(string=u"入库单号")
    user_id = fields.Many2one('res.users', string=u"申请人",default=lambda self: self.env.user, required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人",default=lambda self: self.env.user,)
    # SN = fields.Char()
    SN = fields.Many2many('asset_management.equipment_info',"storge_equipment_ref",string=u"设备SN",required=True,default=_default_SN,domain=[('state','=',u'待入库')])
    state = fields.Selection([
        ('demander', u"需求方申请"),
        ('ass_admin', u"资产管理员"),
        ('ass_admin_manager', u"MA主管"),
        ('owner', u"资产归属人"),
        ('done',u'完成')
    ],string=u"状态",required=True,default='demander')
    owners = fields.Many2many('res.users', string=u'设备归属人', ondelete='set null')
    store_exam_ids = fields.One2many('asset_management.entry_store_examine', 'store_id', string='审批记录')

    def create(self, cr, uid, vals, context=None):
        template_model = self.pool.get('asset_management.equipment_info')
        devices = template_model.browse(cr, uid, vals['SN'][0][2], context=None)
        for device in devices:
            device.state = u'流程中'
        dates = fields.Date.today().split('-')
        date = ''.join(dates)
        template_model = self.pool.get('asset_management.equipment_storage')
        ids = template_model.search(cr, uid, [('storage_id', 'like', date)], context=None)
        stores = template_model.browse(cr, uid, ids, context=None).sorted(key=lambda r: r.storage_id)
        if len(stores):
            vals['storage_id'] = 'S' + str(int(stores[-1].storage_id[1:]) + 1)
        else:
            vals['storage_id'] = 'S' + date + '001'
        return super(equipment_storage, self).create(cr, uid, vals, context=context)

    @api.multi
    def action_to_confirm(self):
        for sn in self.SN:
            if sn.owner:
                self.owners |= sn.owner

        if len(self.owners) == 1:
            if (self.owners[0] == self.user_id or self.owners[0] == self.env['res.groups'].search(
                    [('name', '=', u'资产管理员')], limit=1).users[0]) and self.user_id != self.env['res.groups'].search(
                    ['name', '=', u'资产管理员'], limit=1):
                self.state = 'owner'
                approver_id =self.owners[0]
                self.owners[0] -= approver_id
                self.approver_id = self.owners[0]

            elif self.owners[0] == self.user_id == \
                    self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0] and self.user_id != self.env['res.groups'].search([('name', '=', u'资产管理部门主管')], limit=1).users[0]:
                self.state = 'ass_admin_manager'
                self.owners -= self.user_id
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门主管')], limit=1).users[0]


            elif self.user_id !=self.env['res.groups'].search(
                    [('name', '=', u'资产管理员')], limit=1).users[0]:
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search(
                    [('name', '=', u'资产管理员')], limit=1).users[0]
            else:
                self.state = 'done'
                self.approver_id =None

        elif len(self.owners) > 1:

            if self.user_id in self.owners:
                self.owners -= self.user_id
            if self.env['res.groups'].search([('name', '=', '资产管理员')], limit=1).users[0] in self.owners:
                self.owners -= self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
            self.state = 'ass_admin'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
        else:
            self.state = 'ass_admin'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

    @api.multi
    def action_to_next(self):
        self.env['asset_management.entry_store_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'通过', 'store_id': self.id})
        if self.state == 'owner':
            if len(self.owners):

                approver_id = self.owners[0]
                self.state = 'owner'
                self.owners -= approver_id
                self.approver_id = approver_id
            else:
                self.state = 'ass_admin_manager'
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门主管')], limit=1).users[0]

        elif self.state == 'ass_admin':
            approver_id = self.owners[0]
            self.state = 'owner'
            self.owners -= approver_id
            self.approver_id = approver_id

        elif self.state == 'ass_admin_manager':
            self.state = 'done'
            for device in self.SN:
                device.state = u'已入库'
            self.approver_id = None

    @api.multi
    def action_to_demander(self):
        self.state = 'demander'
        self.env['asset_management.get_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'拒绝', 'store_id': self.id})
        self.approver_id = self.user_id



class equipment_lend(models.Model):
    _name = 'asset_management.equipment_lend'
    _rec_name = 'lend_id'

    def _default_SN(self):
        return self.env['asset_management.equipment_info'].browse(self._context.get('active_ids'))

    @api.multi
    def subscribe(self):
        return {'aaaaaaaaaaaaaa'}

    lend_id = fields.Char(string=u"借用单号")
    user_id = fields.Many2one('res.users', string=u"申请人",default=lambda self: self.env.user,required=True)
    #user_id = fields.Many2one('res.users', string=u"申请人",required=True)
    approver_id = fields.Many2one('res.users',default=lambda self: self.env.user,string=u"审批人")
    SN = fields.Many2many('asset_management.equipment_info',"lend_equipment_ref", string=u"设备SN",default=_default_SN,required=True)
    state = fields.Selection([
            ('demander', u"需求方申请"),
            ('ass_owner', u"资产归属人"),
            ('ass_admin', u"资产管理员"),
            ('dem_leader', u"需求方直属部门领导"),
            ('dem_leader_manager', u"需求方直属主管"),# 副总裁级
            ('ass_director', u"资产管理部门负责人"),
            ('ass_admin_manager', u"资产管理部门主管"),  # 副总裁级MA
        ('done', u'结束'),
    ], string=u"状态", required=True,default='demander')
    lend_date = fields.Date(string=u"借用日期",required=True)
    promise_date = fields.Date(string=u"承诺归还日期",required=True)
    actual_date = fields.Date(string=u"实际归还日期",required=True)
    lend_purpose = fields.Char(string=u"借用目的",required=True)
    owners = fields.Many2many('res.users',string=u"归属人们")
    lend_exam_ids = fields.One2many('asset_management.lend_examine','lend_id',string='审批记录')

    def create(self, cr, uid, vals, context=None):
        template_model = self.pool.get('asset_management.equipment_info')
        devices = template_model.browse(cr, uid, vals['SN'][0][2], context=None)
        for device in devices:
            device.state = u'借用'
        dates = fields.Date.today().split('-')
        date = ''.join(dates)
        template_model = self.pool.get('asset_management.equipment_lend')
        ids = template_model.search(cr, uid, [('lend_id', 'like', date)], context=None)
        lends = template_model.browse(cr, uid, ids, context=None).sorted(key=lambda r: r.lend_id)
        if len(lends):
            vals['lend_id'] = 'L' + str(int(lends[-1].lend_id[1:]) + 1)
        else:
            vals['lend_id'] = 'L' + date + '001'
        return super(equipment_lend, self).create(cr, uid, vals, context=context)


    @api.multi
    def action_to_confirm(self):
        for sn in self.SN:
            if sn.equipment_use == u"公共备件":
                continue
            elif sn.equipment_use == u"专用备件":
                self.owners |= sn.owner

        if len(self.owners) == 1:#改动一去掉 .user[0]
            if (self.owners[0] == self.user_id or self.owners[0] == self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1))\
                    and self.user_id != self.env['res.groups'].search(\
                   ['name', '=', u'资产管理员'], limit=1):
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
                self.state = 'ass_admin'
            elif self.owners[0] == self.user_id == \
                    self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0] and self.user_id != \
                    self.user_id.employee_ids[0].department_id.manager_id:
                self.approver_id = self.user_id
                self.state = 'dem_leader'

            elif self.userb_id != self.owners[0]:
                self.approver_id = self.owners[0]
                self.state = 'ass_owner'
                self.owners -= self.approver_id#没有归属人了

        elif len(self.owners) > 1:
            if self.user_id in self.owners:
                self.owners -= self.user_id

            if self.env['res.groups'].search([('name', '=', '资产管理员')], limit=1).users[0] in self.owners:
                self.owners -= self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

            if self.user_id.employee_ids[0].department_id.manager_id.user_id in self.owners:
                self.owners -= self.user_id.employee_ids[0].department_id.manager_id.user_id

            if len(self.owners)>0:
                self.state = 'ass_owner'
                self.approver_id = self.owners[0]
                self.owners -= self.approver_id#如果归属人还剩两个
            elif len(self.owners)==0:
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

        elif len(self.owners) == 0:
            self.state = 'ass_admin'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

        else:
            print '<1' * 80

    @api.multi
    def action_to_next(self):
        if self.state == 'ass_owner':
            if len(self.owners):
                self.state = 'ass_owner'
                self.approver_id = self.owners[0]
                self.owners -= self.approver_id
            else:
                if self.user_id !=self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]:
                    self.state = 'ass_admin'
                    self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
                    print self.approver_id.name
                else :
                    self.state = 'dem_leader'
                    self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id
                    print self.approver_id.name

        elif self.state == 'ass_admin':
            if self.user_id != self.user_id.employee_ids[0].department_id.manager_id.user_id:
                self.state = 'dem_leader'
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id
                print self.approver_id.name
            else:
                self.state = 'dem_leader_manager'
                if self.user_id.employee_ids[0].department_id.parent_id.manager_id.job_id.name == u'总经理':
                    self.approver_id = self.user_id.employee_ids[0].department_id.parent_id.manager_id.user_id
                else:
                    self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id

        elif self.state == 'dem_leader':
            self.state = 'dem_leader_manager'
            if self.user_id.employee_ids[0].department_id.parent_id.manager_id.job_id.name == u'总经理':
                self.approver_id = self.user_id.employee_ids[0].department_id.parent_id.manager_id.user_id
            else:
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id

        elif self.state == 'dem_leader_manager':
            self.state = 'ass_director'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门负责人')], limit=1).users[0]
            print self.approver_id.name
        elif self.state == 'ass_director':
            self.state = 'ass_admin_manager'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门主管')], limit=1).users[0]
            print self.approver_id.name
        elif self.state == 'ass_admin_manager':
            self.state = 'done'
            for device in self.SN:
                device.state = u'借用'
                self.approver_id = None

            # self.approver_id = self.user_id

        self.env['asset_management.lend_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'通过', 'lend_id': self.id})


    @api.multi
    def action_to_demander(self):
        self.state = 'demander'
        self.approver_id = self.user_id
        self.env['asset_management.lend_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'拒绝', 'lend_id': self.id})


class equipment_get(models.Model):
    _name = 'asset_management.equipment_get'
    _rec_name = 'get_id'

    def _default_SN(self):
        return self.env['asset_management.equipment_info'].browse(self._context.get('active_ids'))
    get_id = fields.Char(string=u"领用单号")
    user_id = fields.Many2one('res.users', string=u"申请人", default=lambda self: self.env.user,required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人",default=lambda self: self.env.user)
    SN = fields.Many2many('asset_management.equipment_info',"get_equipment_ref",string=u"设备SN", default=_default_SN,required=True)
    state = fields.Selection([
             ('demander', u"需求方申请"),
             ('ass_owner', u"资产归属人"),
             ('ass_admin', u"资产管理员"),
             ('dem_leader', u"需求方直属部门领导"),
             ('ass_director', u"资产管理部门负责人"),
             ('ass_admin_manager', u"资产管理部门主管"),  # 副总裁级MA
        ('done',u'结束')
    ], string=u"状态", required=True,default='demander')
    get_date = fields.Date(string=u"领用日期",)
    get_purpose = fields.Char(string=u"领用目的",required=True)
    owners = fields.Many2many('res.users',string=u'设备归属人',ondelete = 'set null')
    get_exam_ids = fields.One2many('asset_management.get_examine','get_id',string='审批记录')

    def create(self, cr, uid, vals, context=None):
        template_model = self.pool.get('asset_management.equipment_info')
        print vals['SN'][0][2]
        devices = template_model.browse(cr, uid, vals['SN'][0][2], context=None)
        for device in devices:
            device.state = u'领用'
        dates = fields.Date.today().split('-')
        date = ''.join(dates)
        template_model = self.pool.get('asset_management.equipment_get')
        ids = template_model.search(cr, uid, [('get_id', 'like', date)], context=None)
        gets = template_model.browse(cr, uid, ids, context=None).sorted(key=lambda r: r.get_id)
        if len(gets):
            vals['get_id'] = 'G' + str(int(gets[-1].get_id[1:]) + 1)
        else:
            vals['get_id'] = 'G' + date + '001'
        return super(equipment_get, self).create(cr, uid, vals, context=context)

    @api.multi
    def subscribe(self):
        # for sn in self.SN:
        #     sn.state = '领用'

        return {}

    @api.multi
    def action_to_confirm(self):
        owners = []
        for sn in self.SN:
            if sn.owner:
                self.owners |= sn.owner

        if len(self.owners) ==1:
            if  (self.owners[0] == self.user_id or self.owners[0] == self.env['res.groups'].search([('name','=',u'资产管理员')],limit=1).users[0]) and self.user_id != self.env['res.groups'].search(['name','=',u'资产管理员'],limit=1):
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search([('name','=',u'资产管理员')],limit=1).users[0]

            elif self.owners[0] == self.user_id  == self.env['res.groups'].search([('name','=',u'资产管理员')],limit=1).users[0] and self.user_id != self.user_id.employee_ids[0].department_id.manager_id:
                self.state = 'dem_leader'
                self.approver_id = self.user_id

            elif self.user_id != self.owners[0]:
                approver_id = self.owners[0]
                self.state = 'ass_owner'
                self.owners -= approver_id
                self.approver_id = approver_id

        elif len(self.owners)>1:

            if self.user_id in self.owners:
                self.owners -= self.user_id
            if self.env['res.groups'].search([('name','=','资产管理员')],limit=1).users[0] in self.owners:
                self.owners -= self.env['res.groups'].search([('name','=',u'资产管理员')],limit=1).users[0]

            if self.user_id.employee_ids[0].department_id.manager_id.user_id in self.owners:
                self.owners -= self.user_id.employee_ids[0].department_id.manager_id.user_id
            if len(self.owners):
                approver_id = self.owners[0]
                self.state = 'ass_owner'
                self.owners -= approver_id
                self.approver_id = approver_id
            else:
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
        else:
            if self.user_id != self.env['res.groups'].search([('name','=',u'资产管理员')],limit=1).users[0]:
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search([('name','=',u'资产管理员')],limit=1).users[0]
            else:
                self.state = 'dem_leader'
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id


    @api.multi
    def action_to_next(self):
        self.env['asset_management.get_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'通过', 'get_id': self.id})
        if self.state == 'ass_owner':
            if len(self.owners):

                approver_id = self.owners[0]
                self.state = 'ass_owner'
                self.owners -= approver_id
                self.approver_id = approver_id
            elif self.user_id == self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]:
                self.state = 'dem_leader'
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id
            else:
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

        elif self.state == 'ass_admin':
            if self.user_id != self.user_id.employee_ids[0].department_id.manager_id.user_id:
                self.state = 'dem_leader'
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id
            else:
                self.state = 'ass_director'
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门负责人')], limit=1).users[0]
        elif self.state == 'dem_leader':

            self.state = 'ass_director'
            self.approver_id = self.env['res.groups'].search([('name','=',u'资产管理部门负责人')],limit=1).users[0]

        elif self.state == 'ass_director':
            self.state = 'ass_admin_manager'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门主管')], limit=1).users[0]

        elif self.state == 'ass_admin_manager':
            self.state = 'done'
            for device in self.SN:
                device.state = u'领用'
            self.approver_id = None


    @api.multi
    def action_to_demander(self):
        self.state = 'demander'
        self.env['asset_management.get_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'拒绝', 'get_id': self.id})
        self.approver_id = self.user_id

class equipment_it_apply(models.Model):
    _name = 'asset_management.equipment_it_apply'
    _rec_name = 'apply_id'

    def _default_SN(self):
        return self.env['asset_management.equipment_info'].browse(self._context.get('active_ids'))

    @api.multi
    def subscribe(self):
        return {'aaaaaaaaaaaaaa'}

    apply_id = fields.Char(string=u"申请IT环境单号")
    user_id = fields.Many2one('res.users', string=u"申请人", required=True)
    approver_id = fields.Many2one('res.users', string=u"审批人")
    SN = fields.Many2many('asset_management.equipment_info',"IT_equipment_ref" ,string=u"设备SN",default=_default_SN, required=True)
    state = fields.Selection([
        ('demander', u"需求方申请"),
        ('ass_owner', u"资产归属人"),
        ('ass_admin', u"资产管理员"),
        ('dem_leader', u"需求方直属部门领导"),
        ('ass_director', u"资产管理部门负责人"),
        ('ass_admin_manager', u"资产管理部门主管"),  # 副总裁级MA
        ('done', u'结束')
    ], string=u"状态", required=True, default='demander')
    use_begin = fields.Date(string=u"使用开始时间",required=True)
    use_over = fields.Date(string=u"使用结束时间",required=True)
    up_date = fields.Date(string=u"设备上架时间",required=True)
    down_date = fields.Date(string=u"设备下架时间",required=True)
    tester = fields.Many2one('res.users',string=u"测试人员",required=True)
    # 这个需要邮件提醒
    application_purpose = fields.Char(string=u"申请目的",required=True)
    owners = fields.Many2many('res.users',string=u"归属人们")
    apply_exam_ids = fields.One2many('asset_management.it_examine','IT_id',string='审批记录')

    def create(self, cr, uid, vals, context=None):
        template_model = self.pool.get('asset_management.equipment_info')
        devices = template_model.browse(cr, uid, vals['SN'][0][2], context=None)
        for device in devices:
            device.state = u'IT环境'
        dates = fields.Date.today().split('-')
        date = ''.join(dates)
        template_model = self.pool.get('asset_management.equipment_it_apply')
        ids = template_model.search(cr, uid, [('apply_id', 'like', date)], context=None)
        applys = template_model.browse(cr, uid, ids, context=None).sorted(key=lambda r: r.apply_id)
        if len(applys):
            vals['apply_id'] = 'I' + str(int(applys[-1].apply_id[1:]) + 1)
        else:
            vals['apply_id'] = 'I' + date + '001'
        return super(equipment_it_apply, self).create(cr, uid, vals, context=context)

    @api.multi
    def action_to_confirm(self):
        for sn in self.SN:
            if sn.equipment_use == u"公共备件":
                continue
            elif sn.equipment_use == u"专用备件":
                self.owners |= sn.owner

        if len(self.owners) == 1:  # 改动一去掉 .user[0]
            if (self.owners[0] == self.user_id or self.owners[0] == self.env['res.groups'].search(
                    [('name', '=', u'资产管理员')], limit=1)) \
                    and self.user_id != self.env['res.groups'].search( \
                            ['name', '=', u'资产管理员'], limit=1):
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
                self.state = 'ass_admin'
            elif self.owners[0] == self.user_id == \
                    self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0] and self.user_id != \
                    self.user_id.employee_ids[0].department_id.manager_id:
                self.approver_id = self.user_id
                self.state = 'dem_leader'

            elif self.userb_id != self.owners[0]:
                self.approver_id = self.owners[0]
                self.state = 'ass_owner'
                self.owners -= self.approver_id  # 没有归属人了

        elif len(self.owners) > 1:
            if self.user_id in self.owners:
                self.owners -= self.user_id

            if self.env['res.groups'].search([('name', '=', '资产管理员')], limit=1).users[0] in self.owners:
                self.owners -= self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

            if self.user_id.employee_ids[0].department_id.manager_id.user_id in self.owners:
                self.owners -= self.user_id.employee_ids[0].department_id.manager_id.user_id

            if len(self.owners) > 0:
                self.state = 'ass_owner'
                self.approver_id = self.owners[0]
                self.owners -= self.approver_id  # 如果归属人还剩两个
            elif len(self.owners) == 0:
                self.state = 'ass_admin'
                self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

        elif len(self.owners) == 0:
            self.state = 'ass_admin'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]

        else:
            print '<1' * 80

    @api.multi
    def action_to_next(self):
        if self.state == 'ass_owner':
            if len(self.owners):
                self.state = 'ass_owner'
                self.approver_id = self.owners[0]
                self.owners -= self.approver_id
            else:
                if self.user_id != self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]:
                    self.state = 'ass_admin'
                    self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理员')], limit=1).users[0]
                    print self.approver_id.name
                else:
                    self.state = 'dem_leader'
                    self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id
                    print self.approver_id.name

        elif self.state == 'ass_admin':
            if self.user_id != self.user_id.employee_ids[0].department_id.manager_id.user_id:
                self.state = 'dem_leader'
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id
                print self.approver_id.name
            else:
                self.state = 'dem_leader_manager'
                if self.user_id.employee_ids[0].department_id.parent_id.manager_id.job_id.name == u'总经理':
                    self.approver_id = self.user_id.employee_ids[0].department_id.parent_id.manager_id.user_id
                else:
                    self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id

        elif self.state == 'dem_leader':
            self.state = 'dem_leader_manager'
            if self.user_id.employee_ids[0].department_id.parent_id.manager_id.job_id.name == u'总经理':
                self.approver_id = self.user_id.employee_ids[0].department_id.parent_id.manager_id.user_id
            else:
                self.approver_id = self.user_id.employee_ids[0].department_id.manager_id.user_id

        elif self.state == 'dem_leader_manager':
            self.state = 'ass_director'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门负责人')], limit=1).users[0]
            print self.approver_id.name
        elif self.state == 'ass_director':
            self.state = 'ass_admin_manager'
            self.approver_id = self.env['res.groups'].search([('name', '=', u'资产管理部门主管')], limit=1).users[0]
            print self.approver_id.name
        elif self.state == 'ass_admin_manager':
            self.state = 'done'
            # self.approver_id = None
            for device in self.SN:
                device.state = u'IT环境'
                self.approver_id = None
            # self.approver_id = self.user_id

        self.env['asset_management.it_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'通过', 'IT_id': self.id})

    @api.multi
    def action_to_demander(self):
        self.state = 'demander'
        self.approver_id = self.user_id
        self.env['asset_management.it_examine'].create(
            {'approver_id': self.approver_id.id, 'result': u'拒绝', 'IT_id': self.id})


class entry_store_examine(models.Model):
    _name='asset_management.entry_store_examine'
    # _rec_name = 'exam_num'

    # exam_num = fields.Char(sting='审批id')
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
    # _rec_name = 'exam_num'
    #
    # exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users', required='True', string='审批人')
    date = fields.Date(string='审批时间',default=lambda self:fields.Date.today())
    result = fields.Selection([
        (u'通过', u"通过"),
        (u'拒绝', u"拒绝"),

    ], string=u"通过")
    lend_id = fields.Many2one('asset_management.equipment_lend', string='借用单')
    reason = fields.Char(string='原因')

class get_examine(models.Model):
    _name = 'asset_management.get_examine'
    # _rec_name = 'exam_num'
    #
    # exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users', required='True', string='审批人')
    date = fields.Date(string='审批时间',default=lambda self:fields.Date.today())
    result = fields.Selection([
        (u'通过', u"通过"),
        (u'拒绝', u"拒绝"),

    ], string=u"通过")
    get_id = fields.Many2one('asset_management.equipment_get', string='领用')
    reason = fields.Char(string='原因')

class IT_examine(models.Model):
    _name = 'asset_management.it_examine'
    # _rec_name = 'exam_num'
    #
    # exam_num = fields.Char(sting='审批id')
    approver_id = fields.Many2one('res.users', required='True', string='审批人')
    date = fields.Date(string='审批时间',default=lambda self:fields.Date.today())
    result = fields.Selection([
        (u'通过', u"通过"),
        (u'拒绝', u"拒绝"),

    ], string=u"通过")
    IT_id = fields.Many2one('asset_management.equipment_it_apply', string='IT环境申请单')
    reason = fields.Char(string='原因')
