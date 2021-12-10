//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        page: 1,
        processing: false,
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });

        // that.setData({
        //     banners: [
        //         {
        //             "id": 1,
        //             "pic_url": "/images/food.jpg"
        //         },
        //         {
        //             "id": 2,
        //             "pic_url": "/images/food.jpg"
        //         },
        //         {
        //             "id": 3,
        //             "pic_url": "/images/food.jpg"
        //         }
        //     ],
        //     categories: [
        //         {id: 0, name: "全部"},
        //         {id: 1, name: "川菜"},
        //         {id: 2, name: "东北菜"},
        //     ],
        //     activeCategoryId: 0,
        //     goods: [
        //         {
        //             "id": 1,
        //             "name": "小鸡炖蘑菇-1",
        //             "min_price": "15.00",
        //             "price": "15.00",
        //             "pic_url": "/images/food.jpg"
        //         },
        //         {
        //             "id": 2,
        //             "name": "小鸡炖蘑菇-1",
        //             "min_price": "15.00",
        //             "price": "15.00",
        //             "pic_url": "/images/food.jpg"
        //         },
        //         {
        //             "id": 3,
        //             "name": "小鸡炖蘑菇-1",
        //             "min_price": "15.00",
        //             "price": "15.00",
        //             "pic_url": "/images/food.jpg"
        //         },
        //         {
        //             "id": 4,
        //             "name": "小鸡炖蘑菇-1",
        //             "min_price": "15.00",
        //             "price": "15.00",
        //             "pic_url": "/images/food.jpg"
        //         }
        //
        //     ],
        //     loadingMoreHidden: false
        // });
    },

    onShow: function () {
        this.getBannerAndCat()
    },

    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    listenerSearchInput: function (e) {
        this.setData({
            searchInput: e.detail.value
        });
    },
    toSearch: function (e) {
        this.setData({
            p: 1,
            goods: [],
            loadingMoreHidden: true
        });
        this.getFoodList();
    },
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    getBannerAndCat: function () {
        let that = this
        wx.request({
            url: app.buildUrl('/food/index'),
            header: app.getRequestHeader(),
            success: function (res) {
                let resp = res.data;
                if (resp.code != 200) {
                    app.alert({'content': resp.msg});
                    return;
                }
                that.setData({
                    banners: resp.data.banner_list,
                    categories: resp.data.cat_list
                });
                that.getFoodList();
            }
        })
    },
    catClick: function (e) {
        this.setData({
            activeCategoryId: e.currentTarget.id,
            page: 1,
            goods: [],
            loadingMoreHidden: true
        });
        this.getFoodList();
    },
    // 上拉加载更多
    onReachBottom: function () {
        let that = this;
        setTimeout(function () {
            that.getFoodList();
        }, 500);
    },
    getFoodList: function () {
        let that = this;

        if (that.data.processing) {
            return;
        }

        if (!that.data.loadingMoreHidden) {
            return;
        }

        that.setData({
            processing: true
        });

        wx.request({
            url: app.buildUrl('/food/search'),
            header: app.getRequestHeader(),
            data: {
                cat_id: that.data.activeCategoryId,
                mix_kw: that.data.searchInput,
                page: that.data.page,
            },
            success: function (res) {
                let resp = res.data;
                if (resp.code != 200) {
                    app.alert({'content': resp.msg});
                    return;
                }
                let goods = resp.data.list;
                that.setData({
                    goods: that.data.goods.concat(goods),
                    page: that.data.page + 1,
                    processing: false
                });
                if (resp.data.has_more === 0) {
                    that.setData({
                        loadingMoreHidden: false
                    });
                }
            }
        });
    }

});
