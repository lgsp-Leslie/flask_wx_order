//获取应用实例
var app = getApp();
Page({
    data: {},
    onLoad() {

    },
    onShow() {
        this.getInfo();
    },
    getInfo(){
        var that = this
        wx.request({
            url: app.buildUrl('/member/info'),
            header: app.getRequestHeader(),
            success(res) {
                let resp = res.data
                if (resp.code !== 200){
                    alert({'content': resp.msg})
                    return;
                }
                that.setData({
                    user_info: resp.data.info
                })
            }
        })
    }
});