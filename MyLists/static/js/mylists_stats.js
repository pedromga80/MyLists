

$(document).ready(function () {
    // --- Canvas Data -------------------------------------------------
    let time_data = $('#time-spent-pie').attr('values').split(', ');
    let seasons_data = $('#seasons-graph-data').attr('values').split(', ');
    let episodes_data = $('#episodes-graph-data').attr('values').split(', ');


    // --- Time sent pie graph -----------------------------------------
    let config_pie = {
        type: 'pie',
        data: {
            datasets: [{
                data: time_data,
                backgroundColor: ['#216e7d', '#945141', '#8c7821'],
                borderColor: 'black',
                borderWidth: 1,
                label: 'by_media'
            }],
            labels: ['Series', 'Anime', 'Movies']
        },
        options: {
            events: false,
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500,
                easing: "easeOutQuart",
                onComplete: function () {
                    let ctx = this.chart.ctx;
                    ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontStyle,
                        Chart.defaults.global.defaultFontFamily);
                    ctx.textAlign = 'center';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';

                    this.data.datasets.forEach(function (dataset) {
                        for (let i = 0; i < dataset.data.length; i++) {
                            let model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                                total = dataset._meta[Object.keys(dataset._meta)[0]].total,
                                mid_radius = model.innerRadius + (model.outerRadius - model.innerRadius) / 2,
                                start_angle = model.startAngle,
                                end_angle = model.endAngle,
                                mid_angle = start_angle + (end_angle - start_angle) / 2;

                            let x = mid_radius * Math.cos(mid_angle);
                            let y = mid_radius * Math.sin(mid_angle);

                            ctx.fillStyle = '#fff';
                            if (i === 3) { // Darker text color for lighter background
                                ctx.fillStyle = '#444';
                            }
                            let percent = String(Math.round(dataset.data[i] / total * 100)) + "%";
                            //Don't Display If Legend is hide or value is 0
                            if (dataset.data[i] !== 0 && dataset._meta[0].data[i].hidden !== true) {
                                ctx.fillText(dataset.data[i] + " h", model.x + x, model.y + y);
                                // Display percent in another line, line break doesn't work for fillText
                                ctx.fillText(percent, model.x + x, model.y + y + 23);
                            }
                        }
                    });
                }
            },
            legend: {
                position: 'bottom',
                labels: {
                    fontColor: '#e2e2e2',
                    fontSize: 14,
                }
            },
            title: {
                display: true,
                text: 'Watched time by media in hours:',
                position: 'top',
                fontColor: '#e2e2e2',
                fontSize: 18,
                fontStyle: 'normal',
            },
        }
    };
    let ctx_pie = document.getElementById('media-time').getContext('2d');
    new Chart(ctx_pie, config_pie);


    // --- Total eps/seasons watched -----------------------------------
    let config_eps = {
        type: 'bar',
        data: {
            datasets: [{
                data: seasons_data,
                backgroundColor: ['#216e7d', '#945141'],
                borderColor: 'black',
                yAxisID: 'y-axis-1'
            },
                {
                    data: episodes_data,
                    backgroundColor: ['#216e7d', '#945141'],
                    borderColor: 'black',
                    yAxisID: 'y-axis-2'
                }],
            labels: ['Series', 'Anime']
        },
        options: {
            events: false,
            responsive: true,
            maintainAspectRatio: false,
            tooltips: {
                enabled: false
            },
            hover: {
                animationDuration: 0
            },
            animation: {
                duration: 1,
                onComplete: function () {
                    let chartInstance = this.chart,
                        ctx = chartInstance.ctx;
                    ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize,
                        Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';

                    this.data.datasets.forEach(function (dataset, i) {
                        let meta = chartInstance.controller.getDatasetMeta(i);
                        meta.data.forEach(function (bar, index) {
                            let data = dataset.data[index];
                            ctx.fillText(data, bar._model.x, bar._model.y - 5);
                        });
                    });
                }
            },
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    type: 'linear',
                    display: true,
                    position: 'left',
                    id: 'y-axis-1',
                    ticks: {
                        fontColor: '#e2e2e2',
                        fontSize: 14,
                        beginAtZero: true
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Seasons completed',
                        fontColor: '#e2e2e2',
                        fontSize: 14
                    }
                },
                    {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        id: 'y-axis-2',
                        gridLines: {
                            color: 'grey',
                        },
                        ticks: {
                            fontColor: '#e2e2e2',
                            fontSize: 14,
                            beginAtZero: true
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Episodes watched',
                            fontColor: '#e2e2e2',
                            fontSize: 14
                        }
                    }],
                xAxes: [{
                    ticks: {
                        fontColor: '#e2e2e2',
                        fontSize: 14,
                    }
                }]
            },
            title: {
                display: true,
                text: 'Number of Seasons/Episodes by media:',
                position: 'top',
                padding: 30,
                fontColor: '#e2e2e2',
                fontSize: 18,
                fontStyle: 'normal'
            }
        }
    };
    let ctx_eps = document.getElementById('total-seasons').getContext('2d');
    new Chart(ctx_eps, config_eps);
});
