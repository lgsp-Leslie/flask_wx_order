;
let food_cat_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function (){
        $('.wrap_cat_set .save').click(function () {
            let btn_target = $(this);
            if (btn_target.hasClass('disabled')) {
                common_ops.alert('正在处理，请不要重复提交！');
                return;
            }

            let name_target = $('.wrap_cat_set input[name=name]');
            let name = name_target.val();

            if (!name || name.length < 1) {
                common_ops.tip('请输入符合规范的分类名称', name_target);
                return false;
            }

            let weight_target = $('.wrap_cat_set input[name=weight]');
            let weight = weight_target.val();

            if (!weight || parseInt(weight) < 1) {
                common_ops.tip('请输入不小于1的权重值', weight_target);
                return false;
            }

            btn_target.addClass("disabled");

            let data = {
                name: name,
                weight: weight,
                id: $('.wrap_cat_set input[name=id]').val()
            }
            $.ajax({
                url: common_ops.buildUrl("edit"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass('disabled');
                    let callback = null;
                    if (res.code === 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("list");
                        }
                    }
                    common_ops.alert(res.msg, callback)
                }
            })

        });

    }
};

$(document).ready(function (){
    food_cat_set_ops.init();
});
