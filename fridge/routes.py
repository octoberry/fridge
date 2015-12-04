# coding=utf-8
import json

from bson import ObjectId
from flask import request
from fridge.app import app
from fridge.forms import ItemForm
from fridge.models import Item, ItemController
from product.find import Items


@app.route('/cart/items', methods=['POST'])
def cart_items():
    data = json.loads(request.data)
    form = ItemForm.from_json(data)
    if form.validate():
        print 'creating product'
        item = Item(**form.data)
        item.save()
        return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return json.dumps({'error': 'can not add product'}), 400, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/items', methods=['GET'])
def cart_items_list():
    shop = request.args.get('shop', None)
    if shop:
        return json.dumps({
            "@tfype": "ProductListCardObject",
            "id": "unique_id_1234",
            "type": "product_list_formed",
            "score": 100500,
            "storeItems": [
                {
                    "storeId": "storeId",
                    "storeName": u"Утконос",
                    "price_list": [
                        {
                            "@type": "PriceListPosition",
                            "id": "unique_item_id_1",
                            "price": 20000.0,
                            "img": "milk.png",
                            "description": u"Отличное молоко от альпийских коров.",
                            "count": 3,
                            "currency":
                                {
                                    "@type": "CurrencyObject",
                                    "name": "RUR",
                                    "readable_name": u"Российский рубль",
                                    "minor_units": 100
                                },
                            "short_description": u"Супер-альп молоко. 1л."
                        },
                        {
                            "@type": "PriceListPosition",
                            "id": "unique_item_id_2",
                            "price": 10000.0,
                            "img": "sosison.png",
                            "description": u"Сосисоны супер просто. Покупайте много!",
                            "count": 1,
                            "currency":
                                {
                                    "@type": "CurrencyObject",
                                    "name": "RUR",
                                    "readable_name": "Российский рубль",
                                    "minor_units": 100
                                },
                            "short_description": u"Сосисоны. 10шт."
                        }
                    ]
                },
                {
                    "storeId": "storeId",
                    "storeName": u"Утконос",
                    "price_list": []
                }
            ]
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        xview = request.headers.get('X-Fridge-view', None)
        items = Item.objects
        if xview == 'ios':
            data = ItemController.items_as_ios(items)
        else:
            data = ItemController.items_as_dict(items)
        return json.dumps(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/item/<string:item_id>', methods=['GET'])
def cart_item_get(item_id):
    item = Item.objects.get(id=ObjectId(item_id))
    return json.dumps(item.as_api()), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/item/<string:item_id>', methods=['DELETE'])
def cart_item_del(item_id):
    Item.objects(id=ObjectId(item_id)).delete()
    return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/item/<string:item_id>/define', methods=['GET'])
def cart_item_define(item_id):
    title = request.args.get('title', None)
    item = Item.objects.get(id=ObjectId(item_id))
    if title is None:
        title = item.title
    q, a, s = Items.do(title, json.loads(item.state))
    item.state = json.dumps(s)
    f = False
    if q is None:
        item.shop_name = a[0]
        item.count = a[1]
        item.price = 50
        q = u"Принято!"
        a = []
        f = True
    item.save()
    return json.dumps({'question': q, 'answers': a, 'finished': f}), 200, {'Content-Type': 'application/json; charset=utf-8'}
