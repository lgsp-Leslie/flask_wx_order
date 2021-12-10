var app = getApp();
Page({
    data: {
        statusType: ["待付款", "待发货", "待收货", "待评价", "已完成", "已关闭"],
        status: ["-8", "-7", "-6", "-5", "1", "0"],
        currentType: 0,
        tabClass: ["", "", "", "", "", ""]
    },
    statusTap: function (e) {
        var curType = e.currentTarget.dataset.index;
        this.data.currentType = curType;
        this.setData({
            currentType: curType
        });
        this.onShow();
    },
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/pages/my/order_info"
        })
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载

    },
    onReady: function () {
        // 生命周期函数--监听页面初次渲染完
    },
    onShow: function () {
        var that = this;
        this.getPayOrder();
    },
    onHide: function () {
        // 生命周期函数--监听页面隐藏

    },
    onUnload: function () {
        // 生命周期函数--监听页面卸载

    },
    onPullDownRefresh: function () {
        // 页面相关事件处理函数--监听用户下拉动作

    },
    onReachBottom: function () {
        // 页面上拉触底事件的处理函数

    },
    getPayOrder() {
        let that = this;
        wx.request({
            url: app.buildUrl('/my/order'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
                status: that.data.status[that.data.currentType]
            },
            success(res) {
                let resp = res.data;
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return;
                }
                that.setData({
                    order_list: resp.data.pay_order_list
                })
            }
        });
    },
    toPay(e) {
        let that = this;
        wx.request({
            url: app.buildUrl('/order/pay'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
                order_sn: e.currentTarget.dataset.id
            },
            success(res) {
                let resp = res.data;
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return;
                }
                let pay_info = resp.data.pay_info;
                wx.requestPayment({
                    'timeStamp': pay_info.timeStamp,
                    'nonceStr': pay_info.nonceStr,
                    'package': pay_info.package,
                    'signType': 'MD5',
                    'paySign': pay_info.paySign,
                    'success': function (res) {

                    },
                    'fail': function (res) {
                    }
                })
            }
        });
    },
    onderCancel(e) {
        this.orderOps(e.currentTarget.dataset.id, 'cancel', '确认取消订单吗？')

    },
    orderConfirm(e) {
        this.orderOps(e.currentTarget.dataset.id, 'confirm', '确认收货？')
    },
    orderOps(order_sn, act, msg) {
        let that = this;
        let params = {
            'content': msg,
            'cb_config': () => {
                wx.request({
                    url: app.buildUrl('/order/ops'),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        order_sn: order_sn,
                        act: act
                    },
                    success(res) {
                        let resp = res.data
                        app.alert({"content": resp.msg});
                        if (resp.code !== 200) {
                            that.getPayOrder()
                            return;
                        }
                    }
                })
            }
        };
        app.tip(params);
    }
})
