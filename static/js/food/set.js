;
// let upload_file = {
//     error: function (msg) {
//         common_ops.alert(msg);
//     },
//     success: function (file_key) {
//         if (!file_key) {
//             return;
//         }
//
//         let html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/><span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';
//
//         let pic_target = $('.upload_pic_wrap .pic-each')
//
//         if (pic_target.size() > 0) {
//             pic_target.html(html);
//         } else {
//             $('.upload_pic_wrap').append('<span class="pic-each">' + html + '</span>');
//         }
//
//         food_set_ops.delete_img();
//     }
// }

function error(msg) {
    common_ops.alert(msg);
}

function success(file_key) {
    if (!file_key) {
        return;
    }

    let html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/><span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

    let pic_target = $('.upload_pic_wrap .pic-each')

    if (pic_target.size() > 0) {
        pic_target.html(html);
    } else {
        $('.upload_pic_wrap').append('<span class="pic-each">' + html + '</span>');
    }

    food_set_ops.delete_img();
}

let food_set_ops = {
    init: function () {
        this.ue = null;
        this.eventBind();
        this.initEditor();
        this.delete_img();
    },
    eventBind: function () {
        let that = this;
        let cat_id_target = $('.wrap_food_set select[name=cat_id]');
        let tags_target = $('.wrap_food_set input[name=tags]');

        $('.wrap_food_set .upload_pic_wrap input[name=upfile]').change(function () {
            $('.wrap_food_set .upload_pic_wrap').submit();
        });

        cat_id_target.select2({
            language: 'zh-CN',
            width: '100%'
        });

        tags_target.tagsInput({
            width: 'auto',
            height: 40,
        });

        $('.wrap_food_set .save').click(function () {
            let btn_target = $(this);
            if (btn_target.hasClass('disabled')) {
                common_ops.alert('正在处理，请不要重复提交！');
                return;
            }

            let cat_id = cat_id_target.val();

            let name_target = $('.wrap_food_set input[name=name]');
            let name = name_target.val()

            let price_target = $('.wrap_food_set input[name=price]');
            let price = price_target.val();

            let summary = $.trim(that.ue.getContent());

            let stock_target = $('.wrap_food_set input[name=stock]');
            let stock = stock_target.val();


            let tags = $.trim(tags_target.val());

            if (parseInt(cat_id) < 1) {
                common_ops.tip('请选择分类', cat_id_target);
                return;
            }
            if (name.length < 1) {
                common_ops.tip('请输入符合规范的名称', name_target);
                return;
            }
            if ($(".wrap_food_set .pic-each").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }
            if (summary.length < 10) {
                common_ops.alert('详情不能少于十个字符')
                return;
            }
            if (parseInt(stock) < 1) {
                common_ops.tip('库存必须大于0', stock_target)
                return;
            }

            if (parseFloat(price) < 0) {
                common_ops.tip('请输入符合的价格', price_target);
                return;
            }
            if (tags.length < 1) {
                common_ops.tip('请输入分类', tags_target)
            }

            btn_target.addClass("disabled");


            let data = {
                cat_id: cat_id,
                name: name,
                price: price,
                main_image: $(".wrap_food_set .pic-each .del_image").attr("data"),
                summary: summary,
                stock: stock,
                tags: tags,
                food_id: $(".wrap_food_set input[name=id]").val()
            };

            $.ajax({
                url: common_ops.buildUrl("edit"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    let callback = null;
                    if (res.code === 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("list");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            });


        });


    },
    initEditor: function () {
        let that = this;
        that.ue = UE.getEditor('editor', {
            toolbars: [
                ['undo', 'redo', '|',
                    'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall', '|', 'rowspacingtop', 'rowspacingbottom', 'lineheight'],
                ['customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
                    'directionalityltr', 'directionalityrtl', 'indent', '|',
                    'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
                    'link', 'unlink'],
                ['imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
                    'insertimage', 'insertvideo', '|',
                    'horizontal', 'spechars', '|', 'inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols']

            ],
            enableAutoSave: true,
            saveInterval: 60000,
            zIndex: 4,
            serverUrl: common_ops.buildUrl('/utils/ueditor/upload')
        });
    },
    delete_img: function () {
        $('.wrap_food_set .del_image').unbind().click(function () {
            $(this).parent().remove();
        })
    }
}

$('document').ready(function () {
    food_set_ops.init();
})