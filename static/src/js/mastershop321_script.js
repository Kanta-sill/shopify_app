const base_url = 'https://odoo.website'

function initJQueryWsap(e) {
    var t;
    "undefined" == typeof jQuery ? ((t = document.createElement("SCRIPT")).src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", t.type = "text/javascript", t.onload = e, document.head.appendChild(t)) : e()
}

initJQueryWsap(function () {
    if (window.AllFetchURLWsap == undefined) {
        window.AllFetchURLWsap = base_url;
        notifywhatsappthankyoupage();
    } else {
        console.log("Error Window.AllFetchURLWsap");
    }
});

window.notifywhatsappthankyoupage = function () {
    item = document.querySelectorAll('.list-view-item__title')
    for (var i = 0; i < item.length; i++) {
        item[i].style.height = "40px";
    }

    var shop = Shopify.shop

    function VariantBought(variant, subtotal, customer_id) {
        $.ajax({
            type: 'POST',
            url: 'https://odoo.website/shopify_data/fetch_variant/' + variant + '/' + subtotal + '/' + customer_id + '/' + shop,
            dataType: 'json',
            data: JSON.stringify({jsonrpc: '2.0'}),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete(data) {
                productDetail = JSON.parse(data['responseText'])['result']

                cart_subtotal_name = document.querySelector('.cart-subtotal__title');
                cart_subtotal_price = document.querySelector('.cart-subtotal_price');
                cart_subtotal_name.style.visibility = 'hidden'
                cart_subtotal_price.style.visibility = 'hidden'

                $(document).ready(function () {
                    $("<table style=\"margin-left: 50%;\">\n" +
                        "            <tr>\n" +
                        "                <td>\n" +
                        "                \t<span class=\"cart-subtotal__title1\"></span>\n" +
                        "                </td>\n" +
                        "                <td>\n" +
                        "                \t<span class=\"cart-subtotal_price1\" data-cart-subtotal></span>\n" +
                        "                </td>\n" +
                        "              </tr>\n" +
                        "              <tr class=\"cart-discount__total1\">\n" +
                        "                <td>\n" +
                        "                \t<span class=\"cart-discount__title\" style=\"font-family: Arial; font-size:17px;\">Discount</span>\n" +
                        "                </td>\n" +
                        "                <td>\n" +
                        "                \t<b id=\"cart-discount_price\" style=\"margin-left: 15px;\">-0 VND</b><br/>\n" +
                        "                    <div id=\"cart-discount__list\">\n" +
                        "                    </div>\n" +
                        "                </td>\n" +
                        "            </tr>\n" +
                        "              <tr id=\"cart-discount__total2\">\n" +
                        "                <td>\n" +
                        "                  <b class=\"cart-total__final\">Total</b>\n" +
                        "                </td>\n" +
                        "                <td>\n" +
                        "                  <b id=\"cart-total_price\">0 VND</b>\n" +
                        "                </td>\n" +
                        "              </tr>\n" +
                        "            </table>").insertAfter(cart_subtotal_price)
                });
                document.querySelector('.cart-subtotal__title1').innerHTML = cart_subtotal_name.innerHTML
                document.querySelector('.cart-subtotal_price1').innerHTML = cart_subtotal_price.innerHTML

                if (productDetail['discounts'].length > 0) {
                    document.getElementById('cart-discount_price').innerHTML = '-' + productDetail['final_discount'].toString() + ' VND'
                    document.getElementById('cart-total_price').innerHTML = productDetail['purchase'].toString() + ' VND'

                    dis_html = ''
                    for (var i = 0; i < productDetail['discounts'].length; i++) {
                        dis_html += '<span>' + productDetail['discounts'][i]['discount_program'] + ' (' + productDetail['discounts'][i]['products'].toString() + '): -' + productDetail['discounts'][i]['discount_amount'].toString() + ' VND</span><br/>'
                    }
                    document.getElementById('cart-discount__list').innerHTML = dis_html
                } else {
                    document.getElementsByClassName('cart-discount__total1')[0].style.visibility = 'hidden'
                    document.getElementById('cart-discount__total2').style.display = 'none'
                }
            }
        })
    }

    if (document.baseURI.startsWith('https://' + shop + '/cart')) {
        var cartContents = fetch('/cart.js')
            .then(response => response.json())
            .then(data => {
                variant_list = {}
                variant_list['items'] = []
                for (var i = 0; i < data['items'].length; i++) {
                    variant_list['items'].push({
                        'variant_id': data['items'][i]['id'],
                        'product_id': data['items'][i]['product_id'],
                        'name': data['items'][i]['title'],
                        'quantity': data['items'][i]['quantity'],
                        'price': data['items'][i]['original_price'] / 100
                    })
                }
                variant_list_str = JSON.stringify(variant_list)
                subtotal = data['total_price'] / 100
                var customer_id
                if (window.customerId == "") {
                    customer_id = "No Customer"
                } else {
                    customer_id = window.customerId
                }
                VariantBought(variant_list_str, subtotal, customer_id)
                return data
            });
    }
}

