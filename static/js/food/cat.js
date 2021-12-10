;
let cat_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        let that = this;
        $('.wrap_search select[name=status]').change(function (){
            $('.wrap_search').submit();
        })

        $('.remove').click(function () {
            that.ops('remove', $(this).attr('data-id'))
        });
        $('.recover').click(function () {
            that.ops('recover', $(this).attr('data-id'))
        });
    },
    ops: function (act, id) {
        let callback = {
            'ok': function () {
                $.ajax({
                    url: common_ops.buildUrl('ops'),
                    type: 'PUT',
                    data: {
                        act: act,
                        id: id
                    },
                    dataType: 'json',
                    success: function (res) {
                        let callback = null;
                        if (res.code === 200) {
                            callback = function () {
                                location.reload();
                            }
                        }
                        common_ops.alert(res.msg, callback);
                    }
                })
            }
        };
        common_ops.confirm((act === 'remove' ? '删除确认？' : '恢复确认？'), callback);
    }
}

$(document).ready(function () {
    cat_ops.init();
})