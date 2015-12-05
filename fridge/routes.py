# coding=utf-8
import json

from bson import ObjectId
from flask import request
from fridge.app import app, cart
from fridge.forms import ItemForm
from fridge.models import Item, ItemController, ItemShopController
from fridge.telegram import Telegram
from product.find import Items, GetQuery


@app.route('/cart/items', methods=['POST'])
def cart_items():
    data = json.loads(request.data)
    form = ItemForm.from_json(data)
    if form.validate():
        print 'creating product'
        item = Item(**form.data)
        item.save()
        return json.dumps(item.as_api()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return json.dumps({'error': 'can not add product'}), 400, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/items', methods=['GET'])
def cart_items_list():
    # shop = request.args.get('shop', None)
    if cart.status == 'confirmed':
        xview = request.headers.get('X-Fridge-view', None)
        items = Item.objects
        if xview == 'ios':
            data = ItemShopController.items_as_ios(items)
        else:
            data = ItemShopController.items_as_dict(items)
        return json.dumps(data), 200, {'Content-Type': 'application/json; charset=utf-8'}
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


@app.route('/cart/item/<string:item_id>', methods=['POST'])
def cart_item_update(item_id):
    item = Item.objects.get(id=ObjectId(item_id))
    data = json.loads(request.data)
    form_data = item.to_form_data()
    for d in form_data:
        if d not in data:
            data.update({d: form_data[d]})
    form = ItemForm.from_json(data)
    if form.validate():
        print item.count
        print form.data
        item.title = form.data.title
        item.shop_name = form.data.shop_name
        item.price = form.data.price
        item.count = form.data.count
        item.save()
        Telegram.push(message=u"Список покупок уточнен, добавил %s" % item.shop_name)
    else:
        print form.errors
    item = Item.objects.get(id=ObjectId(item_id))
    return json.dumps(item.as_api()), 200, {'Content-Type': 'application/json; charset=utf-8'}


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
        print a
        item.shop_name = a[0]
        item.count = a[1]
        item.price = float(a[2])
        item.magaz = a[3]
        q = u"Принято!"
        a = []
        f = True
    item.save()
    return json.dumps({'question': q, 'answers': a, 'finished': f}), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/item/<string:item_id>/list', methods=['GET'])
def cart_item_list(item_id):
    item = Item.objects.get(id=ObjectId(item_id))
    items_list = GetQuery(item.title)
    return json.dumps(items_list), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/query', methods=['GET'])
def query():
    q = request.args.get('q', None)
    words = Items.filterWords(q)
    words = list(set(words))
    for w in words:
        item = Item(title=w)
        item.save()
        Telegram.push(message=u"Добавил %s" % w)
    return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart', methods=['POST'])
def cart_update():
    cart.status = 'confirmed'
    Telegram.push(message=u"Корзина сформирована")
    Telegram.push(message=u"Оплатите покупки")
    return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}
