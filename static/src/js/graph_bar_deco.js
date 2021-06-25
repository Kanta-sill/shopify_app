function get_test_graph_bar(result) {
    var productValue = result[0]['products']
    var productQuantity = result[0]['product_quantity']
    var discountValue = result[0]['discounts']
    var discountQuantity = result[0]['discount_quantity']
    var month = result[0]['month']
    var minProduct = (Math.min(...productQuantity) - 1)
    var maxProduct = (Math.max(...productQuantity) + 1)
    var minDiscount = (Math.min(...discountQuantity) - 1)
    var maxDiscount = (Math.max(...discountQuantity) + 1)
    var ctxbar = document.getElementById('discount_graph_bar_id').getContext('2d');
    var myChartBar = new Chart(ctxbar, {
        type: 'bar',
        data: {
            labels: discountValue,
            datasets: [{
                label: 'Top Discount ' + month,
                data: discountQuantity,
                fill: false,
                borderColor: 'green',
                backgroundColor: '#A1F7BB',
            },]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: minDiscount,
                        max: maxDiscount,
                    },
                }],
            },
        }
    });
    var ctxProduct = document.getElementById('product_graph_bar_id').getContext('2d');
    var productChartBar = new Chart(ctxProduct, {
        type: 'bar',
        data: {
            labels: productValue,
            datasets: [{
                label: 'Top Product ' + month,
                data: productQuantity,
                fill: false,
                borderColor: 'green',
                backgroundColor: '#eda634',
            },]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: minProduct,
                        max: maxProduct,
                    },
                }],
            },
        }
    });
}