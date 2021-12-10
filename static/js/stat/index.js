;
let stat_index_ops = {
    init() {
        this.eventBind();
        this.drawChart();
        this.datetimepickerComponent();
    },
    eventBind() {
        $("#search_form_wrap .search").click(() => {
            $('#search_form_wrap').submit();
        });
    },
    // 日期时间选择控件
    datetimepickerComponent() {
        let that = this;
        $.datetimepicker.setLocale('zh')
        params = {
            scrollInput: false,
            scrollMonth: false,
            scrollTime: false,
            dayOfWeekStart: 1,
            lang: 'zh',
            todayButton: true,
            defaultDate: new Date().Format('yyyy-MM-dd'),
            format: 'Y-m-d',
            timepicker: false
        };
        $('#search_form_wrap input[name=date_from]').datetimepicker(params);
        $('#search_form_wrap input[name=date_to]').datetimepicker(params);
    },
    drawChart() {
        charts_ops.setOption();
        $.ajax({
            url: common_ops.buildUrl('/chart/finance'),
            dataType: 'json',
            success(res) {
                charts_ops.drawLine($('#container'), res.data)
            }
        });
    }

};

$(document).ready(function () {
    stat_index_ops.init();
});
