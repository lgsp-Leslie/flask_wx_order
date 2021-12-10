//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [],
        default_address: null,
        yun_price: "0.00",
        pay_price: "0.00",
        total_price: "0.00",
        params: null
    },
    onShow: function () {
        var that = this;
        this.getOrderInfo();
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            params: JSON.parse(e.data)
        });
    },
    createOrder: function (e) {
        wx.showLoading();
        var that = this;
        let data = {
            type: this.data.params.type,
            goods: JSON.stringify(this.data.params.goods),
        };

        wx.request({
            url: app.buildUrl('/food/order'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success(res) {
                let resp = res.data

                wx.hideLoading();

                if (resp.code != 200) {
                    app.alert({'content': resp.msg})
                    return;
                }
                wx.navigateTo({
                    url: "/pages/my/order_list"
                });
            }
        });
    },
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },

    getOrderInfo() {
        let that = this;
        let data = {
            type: this.data.params.type,
            goods: JSON.stringify(this.data.params.goods),
        };
        wx.request({
            url: app.buildUrl('/food/get/order'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success(res) {
                let resp = res.data

                if (resp.code != 200) {
                    app.alert({'content': resp.msg})
                    return;
                }

                that.setData({
                    goods_list: resp.data.food_list,
                    default_address: resp.data.default_address,
                    yun_price: resp.data.yun_price,
                    pay_price: resp.data.pay_price,
                    total_price: resp.data.total_price,
                })
            }
        })
    }

});
