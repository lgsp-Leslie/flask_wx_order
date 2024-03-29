var app = getApp();
Page({
    data: {
        list: [
            {
                date: "2018-07-01 22:30:23",
                order_number: "20180701223023001",
                content: "记得周六发货",
            },
            {
                date: "2018-07-01 22:30:23",
                order_number: "20180701223023001",
                content: "记得周六发货",
            }
        ]
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载

    },
    onShow: function () {
        this.getCommentList();
    },
    getCommentList() {
        let that = this
        wx.request({
            url: app.buildUrl('/my/comment/list'),
            header: app.getRequestHeader(),
            success(res) {
                let resp = res.data
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg})
                    return;
                }
                that.setData({
                    list: resp.data.list
                })
            }
        })
    }
});
