;
let member_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $('.wrap_member_set .save').click(function () {
            let btn_target = $(this);
            if (btn_target.hasClass('disabled')) {
                common_ops.alert('正在处理，请不要重复提交！')
                return;
            }
            let nickname_target = $('.wrap_member_set input[name=nickname]');
            let nickname = nickname_target.val()

            if (nickname.length < 1) {
                common_ops.alert('请输入符合规范的昵称！', nickname_target);
                return;
            }

            btn_target.addClass('disable');
            let data = {
                nickname: nickname,
                id: $('.wrap_member_set input[name=id]').val()
            };
            $.ajax({
                url: common_ops.buildUrl('edit'),
                type: 'PUT',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass('disable');
                    let callback = null;
                    if (res.code === 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("list");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            })
        });
    }
};

$(document).ready(function () {
    member_set_ops.init();
});
