# coding=utf-8
import json

from flask import request
from fridge.app import app, state
from fridge.forms import ProductForm
from product.find import Beer


@app.route('/cart/items', methods=['POST'])
def cart_items():
    data = json.loads(request.data)
    form = ProductForm.from_json(data)
    if form.validate():
        print 'creating product'
        return json.dumps({}), 200
    else:
        raise json.dumps({'error': 'can not add product'}), 400


@app.route('/cart/items', methods=['GET'])
def cart_items_list():
    return json.dumps({
        "@type": "ProductListCardObject",
        "id": "unique_id_1234",
        "type": "product_list_raw",
        "score": 100500,
        "price_list": [
            {
                "@type": "PriceListPosition",
                "id": "unique_item_id_1",
                "price": 20000.0,
                "img": "milk.png",
                "description": "Отличное молоко от альпийских коров.",
                "count": 3,
                "currency":
                    {
                        "@type": "CurrencyObject",
                        "name": "RUR",
                        "readable_name": "Российский рубль",
                        "minor_units": 100
                    },
                "short_description": "Супер-альп молоко. 1л."
            },
            {
                "@type": "PriceListPosition",
                "id": "unique_item_id_2",
                "price": 10000.0,
                "img": "sosison.png",
                "description": "Сосисоны супер просто. Покупайте много!",
                "count": 1,
                "currency":
                    {
                        "@type": "CurrencyObject",
                        "name": "RUR",
                        "readable_name": "Российский рубль",
                        "minor_units": 100
                    },
                "short_description": "Сосисоны. 10шт."
            }
        ]
    }), 200


@app.route('/cart/item/<string:item_id>', methods=['GET', 'DELETE'])
def cart_item(item_id):
    print item_id
    return '', 200


@app.route('/product/find', methods=['GET'])
def product_find():
    title = request.args.get('title')
    if u'пиво' in title:
        q, items, s = Beer.doFirst()
        state.set_state(s)
    else:
        q, items, s = Beer.do(title, state.get_state())
        state.set_state(s)
    return "%s, %s" % (q, items), 200
