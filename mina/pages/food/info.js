//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
let utils = require('../../utils/util.js');

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax: 1,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 4,
        commentCount: 2,
        info: '',
    },
    onLoad: function (e) {
        var that = this;

        that.setData({
            id: e.id
        });

        that.setData({
            // "info": {
            //     "id": 1,
            //     "name": "小鸡炖蘑菇",
            //     "summary": '<p>多色可选的马甲</p><p><img src="http://www.timeface.cn/uploads/times/2015/07/071031_f5Viwp.jpg"/></p><p><br/>相当好吃了</p>',
            //     "total_count": 2,
            //     "comment_count": 2,
            //     "stock": 2,
            //     "price": "80.00",
            //     "main_image": "/images/food.jpg",
            //     "pics": ['/images/food.jpg', '/images/food.jpg']
            // },
            // buyNumMax: 2,
            commentList: [
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                },
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                }
            ]
        });

        // WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);

    },
    onShow: function () {
        this.getInfo();
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    addShopCar: function () {
        let that = this;
        let data = {
            'id': this.data.info.id,
            'number': this.data.buyNumber
        };
        wx.request({
            url: app.buildUrl('/food/cart'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success(res) {
                let resp = res.data;
                app.alert({'content': resp.msg});
                that.setData({
                    hideShopPopup: true
                });
                that.getInfo();
            }
        })
    },
    buyNow: function () {
        let data = {
            goods: [{
                'id': this.data.info.id,
                'price': this.data.info.price,
                'number': this.data.buyNumber,
            }]
        };

        this.setData({
            hideShopPopup: true
        });

        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify(data)
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if (this.data.buyNumber <= this.data.buyNumMin) {
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if (this.data.buyNumber >= this.data.buyNumMax) {
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },

    getInfo: function () {
        let that = this;
        wx.request({
            url: app.buildUrl('/food/info'),
            header: app.getRequestHeader(),
            data: {
                food_id: that.data.id
            },
            success: function (res) {
                let resp = res.data;
                if (resp.code !== 200) {
                    app.alert({
                        'content': resp.msg
                    });
                    return;
                }
                that.setData({
                    info: resp.data.info,
                    buyNumMax: resp.data.stock,
                    shopCarNum: resp.data.cart_number
                });
                WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);
            }
        });
    },
    // 转发分享
    onShareAppMessage() {
        let that = this;
        wx.request({
            url: app.buildUrl('/member/share'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
                url: utils.getCurrentPageUrlWithArgs(),
                device: '微信小程序'
            },
        });
        return {
            title: that.data.info.name,
            path: utils.getCurrentPageUrlWithArgs(),
        };
    }

});
