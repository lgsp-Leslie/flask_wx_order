;
let user_edit_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $(".user_edit_wrap .save").click(function () {

            let btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理，请不要重复提交！");
                return;
            }

            let nickname_target = $(".user_edit_wrap input[name=nickname]");
            let nickname = nickname_target.val()

            let email_target = $(".user_edit_wrap input[name=email]");
            let email = email_target.val()

            if (!nickname || nickname.length < 2) {
                common_ops.tip("昵称不能为空,且不能少于两个字符！", nickname_target);
                return false;
            }

            if (!email || email.length < 2) {
                common_ops.tip("邮箱地址不能为空！", email_target);
                return false;
            }

            btn_target.addClass("disabled");

            let data = {
                nickname: nickname,
                email: email
            };

            $.ajax({
                url: common_ops.buildUrl("edit"),
                type: "PUT",
                data: data,
                dataType: "json",
                success: function (res) {
                    btn_target.removeClass("disabled");
                    let callback = null;
                    if (res.code === 200) {
                        callback = function () {
                            // window.location.href = window.location.href;
                            location.reload();
                        }
                    }
                    common_ops.alert(res.msg, callback)
                }
            })


        });
    }
}

$(document).ready(function () {
    user_edit_ops.init();
});
