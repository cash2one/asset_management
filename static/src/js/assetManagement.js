/**
 * Created by Administrator on 2016-11-2.
 */
openerp.asset_management=function(instance){
    var _t=instance.web._t,
        _lt=instance.web._lt,
        QWeb=instance.web.qweb;
    instance.asset_management={};

    instance.asset_management.Widget=instance.web.Widget.extend({
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
                            self.addBtn(display_name)
                            watch(action_manager,"inner_action",function(pro,action,newVal,oldVal){
                                self.addBtn(newVal.display_name);
                            });
                        }
                    }
                }
            },100)
        },
        //
        addBtn:function(display_name){
            var self=this;
            if(display_name=="设备信息表"){
                var timer=setInterval(function(){
                    var btnParent=$('tr.oe_header_row:last>td:last');
                    if(btnParent.length>0&&($('tr.oe_header_row button.assetM').length==0)){
                        clearInterval(timer);
                        var btn=$("<button class='assetM oe_right'>入库</button>");
                        btnParent.append(btn);
                        btn.click(function(){
                            self.jump();
                        });
                    }
                },100)
            }
        },
        jump:function(){
            var $spans = $('.oe_leftbar li.active~li .oe_menu_text');
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

        start:function(){
        //暂时不需要
        }
    });
    instance.asset_management.widget=new instance.asset_management.Widget();
}