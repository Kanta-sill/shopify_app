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

notifywhatsappthankyoupage = function () {
    item = document.querySelectorAll('.list-view-item__title')
    for (var i = 0; i < item.length; i++) {
        item[i].style.height = "40px";
    }

    const shop = Shopify.shop
    const currency = Shopify.currency["active"]

    function UpdateCheckout(data) {
        $.ajax({
            type: 'POST',
            url: base_url + '/shopify_data/update_checkout/' + shop,
            dataType: 'json',
            data: JSON.stringify({
                'params': data,
            }),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete: function (data) {
                window.location = JSON.parse(data['responseText'])['result']
            }
        })
    }

    if (document.baseURI.startsWith('https://' + shop + '/cart')) {
        $.ajax({
            type: 'GET',
            url: 'https://' + shop + '/cart.js',
            dataType: 'json',
            data: JSON.stringify({jsonrpc: '2.0'}),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete: function (data) {
                data_parse = JSON.parse(data['responseText'])
                var customer_id
                if (window.customerId == "") {
                    customer_id = "No Customer"
                } else {
                    customer_id = window.customerId
                }
                VariantBought(data_parse, customer_id)
            }
        })
    }

    function VariantBought(data, customer_id) {
        $.ajax({
            type: 'POST',
            url: base_url + '/shopify_data/fetch_variant/' + customer_id + '/' + shop,
            dataType: 'json',
            data: JSON.stringify({
                'params': data,
            }),
            contentType: 'application/json',
            error: function (request, error) {
                console.log('error')
            },
            complete: function (data) {
                productDetail = JSON.parse(data['responseText'])['result']
                cart_subtotal_name = document.querySelector('.cart-subtotal__title');
                cart_subtotal_price = document.querySelector('.cart-subtotal_price');
                cart_subtotal_name.style.visibility = 'hidden';
                cart_subtotal_price.style.visibility = 'hidden';

                view_cart = '<table style="margin-left: 50%;">\n' +
                    '            <tr>\n' +
                    '                <td>\n' +
                    '                \t<span class="cart-subtotal__title1">{{ \'cart.general.subtotal\' | t }}</span>\n' +
                    '                </td>\n' +
                    '                <td>\n' +
                    '                \t<span class="cart-subtotal_price1" data-cart-subtotal>{{ cart.total_price | money_with_currency }}</span>\n' +
                    '                </td>\n' +
                    '              </tr>\n' +
                    '              <tr class="cart-discount__total1">\n' +
                    '                <td>\n' +
                    '                \t<span class="cart-discount__title" style="font-family: Arial; font-size:17px;">Discount</span>\n' +
                    '                </td>\n' +
                    '                <td>\n' +
                    '                \t<b id="cart-discount_price" style="margin-left: 15px;">-0 VND</b><br/>\n' +
                    '                    <div id="cart-discount__list">\n' +
                    '                    </div>\n' +
                    '                </td>\n' +
                    '            </tr>\n' +
                    '              <tr id="cart-discount__total2">\n' +
                    '                <td>\n' +
                    '                  <b class="cart-total__final">Pre-Total</b>\n' +
                    '                </td>\n' +
                    '                <td>\n' +
                    '                  <b id="cart-total_price">0 VND</b>\n' +
                    '                </td>\n' +
                    '              </tr>\n' +
                    '            </table>'

                $(view_cart).insertAfter(cart_subtotal_price)

                document.querySelector('.cart-subtotal__title1').innerHTML = cart_subtotal_name.innerHTML;
                document.querySelector('.cart-subtotal_price1').innerHTML = cart_subtotal_price.innerHTML;

                if (productDetail['discounts'].length > 0) {

                    document.getElementById('cart-discount_price').innerHTML = '-' + productDetail['final_discount'].toString() + ' ' + currency
                    document.getElementById('cart-discount_price').style.color = productDetail['amount_color']
                    document.getElementById('cart-total_price').innerHTML = productDetail['purchase'].toString() + ' ' + currency
                    document.getElementById('cart-discount__list').style.color = productDetail['voucho_color']
                    document.getElementsByClassName('cart-discount__title')[0].style.color = productDetail['discount_color']
                    discount_html = ''
                    for (var i = 0; i < productDetail['discounts'].length; i++) {
                        discount_html += '<span>' + productDetail['discounts'][i]['discount_program'] + ' (' + productDetail['discounts'][i]['products'].toString() + '): -' + productDetail['discounts'][i]['discount_amount'].toString() + ' ' + currency + '</span><br/>'
                    }
                    document.getElementById('cart-discount__list').innerHTML = discount_html

                } else {
                    document.getElementsByClassName('cart-discount__total1')[0].style.visibility = 'hidden'
                    document.getElementById('cart-discount__total2').style.display = 'none'
                }

                $(".cart__submit").click(function () {
                    $.ajax({
                        type: 'GET',
                        url: 'https://' + shop + '/cart.js',
                        dataType: 'json',
                        data: JSON.stringify({jsonrpc: '2.0'}),
                        contentType: 'application/json',
                        error: function (request, error) {
                            console.log('error')
                        },
                        complete: function (data) {
                            var data_parse = JSON.parse(data['responseText'])
                            if (window.customerId == "") {
                                alert('You must login before checkout')
                                top.location.href = document.location.href;
                            } else {
                                data_parse['discount_program'] = productDetail['discounts']
                                data_parse['customer_id'] = window.customerId
                                data_parse['discount_value'] = productDetail['final_discount']
                                data_parse['total'] = productDetail['purchase']
                                UpdateCheckout(data_parse)
                            }
                        }
                    })
                });
            }
        })
    }
}

