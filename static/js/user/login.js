;
let user_login_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        let that = this
        $(".login_wrap .do-login").click(function () {

            // 防止多次点击提交
            let btn_target = $(this);
            if (btn_target.hasClass("disabled")){
                common_ops.alert("正在处理，请不要重复提交！");
                return;
            }

            let login_name = $(".login_wrap input[name='login_name']").val();
            let login_pwd = $(".login_wrap input[name='login_pwd']").val();

            if (login_name === undefined || login_name.length < 1 || login_pwd === undefined || login_pwd.length < 1) {
                common_ops.alert('用户名或密码不能为空');
                return false;
            }

            btn_target.addClass("disabled");

            $.ajax({
                url: common_ops.buildUrl("/manage/login"),
                type: "POST",
                data: {
                    "login_name": login_name,
                    "login_pwd": login_pwd,
                },
                dataType: "json",
                success: function (res) {
                    btn_target.removeClass("disabled");
                    let callback = null;
                    if (res.code === 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("index");
                        }
                    }
                    that.alert(res.msg, callback)
                }
            });

        });
    },

    alert: function (msg, cb) {
        layer.alert(msg, {
            yes: function (index) {
                if (typeof cb == "function") {
                    cb();
                }
                layer.close(index);
            }
        });
    }

};

$(document).ready(function () {
    user_login_ops.init();
});