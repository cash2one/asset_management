/**
 * Created by Administrator on 2016-11-2.
 */
openerp.asset_management=function(instance){
    var _t=instance.web._t,
        _lt=instance.web._lt,
        QWeb=instance.web.qweb;
    instance.asset_management={};

    instance.asset_management.Widget=instance.web.Widget.extend({
        menuId:-1,//初始化菜单ID
        init:function(){
            var self=this;
            var timer=setInterval(function(){
                var action_manager=instance.client.action_manager;
                if(action_manager){
                    var inner_action=action_manager.inner_action;
                    if(inner_action){
                        var display_name=inner_action.display_name;
                        if(display_name){
                            clearInterval(timer);
                            self.addAction(display_name);
                            watch(action_manager,"inner_action",function(pro,action,newVal,oldVal){
                                self.addAction(newVal.display_name);
                            });
                        }
                    }
                }
            },100)
        },
        //视图加载完成后定义自己的动作
        addAction:function(title){
            var self=this;
            var timer=setInterval(function(){
                var targetSpan=$("#oe_main_menu_navbar ul.navbar-left>li.active>a>span.oe_menu_text");
                if(targetSpan.length){
                    clearInterval(timer);
                    var modelTitle=targetSpan.html().trim();
                    if(modelTitle=="Asset management"||modelTitle=="资产管理"){
                        self.addBtn(title);//添加自定义按钮
                        self.removeBtn(title);//删除按钮
                        self.menuId=targetSpan.parent("a").attr("data-menu");
                    }else{
                        $('#asset_management_removeBtn').remove();
                    }
                }
            },100);
        },
        addBtn:function(display_name){//添加自定义按钮
            var self=this;
            if(display_name=="库存中的设备"){
                var btnParent=$('tr.oe_header_row:last>td:last');
                if(btnParent.length>0&&($('tr.oe_header_row button.assetM').length==0)){
                    var btn=$("<button class='assetM oe_right'>入库</button>");
                    btnParent.append(btn);
                    btn.click(function(){
                        self.jump();
                    });
                }
            }
        },
        jump:function(){
            var $spans = $("div[data-menu-parent="+this.menuId+"] .oe_menu_text");
            $spans.each(function(i,v){
                var text=$(v).html().trim();
                if(text=="storing Menu"||text=="入库单"){
                    $(v).parent("a").trigger("click");
                    var timer=setInterval(function(){
                        if($('.oe_list_buttons>.oe_list_add').length){
                            clearInterval(timer);
                            $('.oe_list_buttons>.oe_list_add').trigger("click");
                        }
                    },100)
                }
            });
        },
        removeBtn:function(display_name){
            if(display_name=="库存中的设备"){
                $('#asset_management_removeBtn').remove();
            }else{
                if($('#asset_management_removeBtn').length==0){
                    $("head").append("<link id='asset_management_removeBtn' rel='stylesheet' href='/asset_management/static/src/css/removeBtn.css' />");
                }
            }
        },
        start:function(){
        //暂时不需要
        }
    });
    instance.asset_management.widget=new instance.asset_management.Widget();
}