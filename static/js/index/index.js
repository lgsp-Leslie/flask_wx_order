;
let dashboard_index_ops = {
    init() {
        this.drawChart();
    },
    drawChart() {
        charts_ops.setOption();
        
        $.ajax({
            url: common_ops.buildUrl('/chart/dashboard'),
            dataType: 'json',
            success(res) {
                charts_ops.drawLine($('#member_order'), res.data);
            }
        });

        $.ajax({
            url: common_ops.buildUrl('/chart/finance'),
            dataType: 'json',
            success(res) {
                charts_ops.drawLine($('#finance'), res.data);
            }
        });

    }
};

$(document).ready(() => {
    dashboard_index_ops.init();
})