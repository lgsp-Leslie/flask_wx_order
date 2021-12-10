;
let account_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        $('.wrap_account_set .save').click(function () {
            let btn_target = $(this);
            if (btn_target.hasClass('disabled')) {
                common_ops.alert('正在处理，请不要重复提交！');
                return;
            }

            let nickname_target = $('.wrap_account_set input[name=nickname]');
            let nickname = nickname_target.val();

            if (!nickname || nickname.length < 2) {
                common_ops.tip('请输入符合规范的昵称', nickname_target);
                return false;
            }

            let mobile_target = $('.wrap_account_set input[name=mobile]');
            let mobile = mobile_target.val();
            let reg = /^(13[0-9]|14[5|7]|15[0|1|2|3|4|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$/;
            if (!mobile || !reg.test(mobile)) {
                common_ops.tip('请输入符合规范的手机号码！', mobile_target);
                return false;
            }

            let email_target = $('.wrap_account_set input[name=email]');
            let email = email_target.val();
            reg = /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/;
            if (!email || !reg.test(email)) {
                common_ops.tip('请输入符合规范的邮箱地址！', email_target);
                return false;
            }

            let login_name_target = $('.wrap_account_set input[name=login_name]');
            let login_name = login_name_target.val();
            if (!login_name || login_name.length < 5) {
                common_ops.tip('请输入符合规范的登录用户名！', login_name_target);
                return false;
            }

            let login_pwd_target = $('.wrap_account_set input[name=login_pwd]');
            let login_pwd = login_pwd_target.val();
            if (!login_pwd || login_pwd.length < 6) {
                common_ops.tip('请输入符合规范的密码！', login_pwd_target);
                return false;
            }
            btn_target.addClass("disabled");

            let data = {
                nickname: nickname,
                mobile: mobile,
                email: email,
                login_name: login_name,
                login_pwd: login_pwd,
                id: $('.wrap_account_set input[name=id]').val()
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
}

$(document).ready(function () {
    account_set_ops.init();
})