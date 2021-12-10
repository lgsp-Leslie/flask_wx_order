;
let user_reset_pwd_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $('#save').click(function () {
            let btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理，请不要重复提交！");
                return;
            }

            let old_pwd_target = $('#old_password');
            let old_pwd = old_pwd_target.val();

            let new_pwd_target = $('#new_password');
            let new_pwd = new_pwd_target.val()

            let re_new_pwd_target = $('#re_new_password');
            let re_new_pwd = re_new_pwd_target.val()

            if (!old_pwd || old_pwd.length < 6) {
                common_ops.tip("旧密码不能为空,且长度不能小于6！", old_pwd_target);
                return false;
            }

            if (!new_pwd || new_pwd.length < 6) {
                common_ops.tip("新密码不能为空，且长度不能小于6！", new_pwd_target);
                return false;
            }
            if (!re_new_pwd || re_new_pwd.length < 6) {
                common_ops.tip("确认新密码不能为空，且长度不能小于6！", re_new_pwd_target);
                return false;
            }
            if (new_pwd !== re_new_pwd) {
                common_ops.tip("两次输入的新密码不一致，请确认！", re_new_pwd_target);
                return false;
            }

            if (new_pwd === old_pwd) {
                common_ops.tip("新密码和旧密码相同，请重新输入！", new_pwd_target);
                return false;
            }

            btn_target.addClass("disabled");

            let data = {
                old_pwd: old_pwd,
                new_pwd: new_pwd,
                re_new_pwd: re_new_pwd
            };

            $.ajax({
                url: common_ops.buildUrl('pwd'),
                type: "PUT",
                data: data,
                dataType: "json",
                success: function (res) {
                    btn_target.removeClass('disabled');
                    let callback = null;
                    if (res.code === 200) {
                        callback = function () {
                            location.reload()
                        }
                    }
                    common_ops.alert(res.msg, callback)
                }
            })


        })
    }
}

$(document).ready(function () {
    user_reset_pwd_ops.init()
})