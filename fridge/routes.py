# coding=utf-8
import json

from bson import ObjectId
from flask import request
from fridge.app import app
from fridge.forms import ItemForm
from fridge.models import Item, ItemController, ItemShopController, Cart, CartController
from fridge.telegram import Telegram
from product.find import Items, GetQuery


@app.route('/cart/items', methods=['POST'])
def cart_items():
    xchat_id = request.headers.get('X-Fridge-chat-id', None)
    if xchat_id is None or xchat_id == {} or xchat_id == "{}":
        xchat_id = app.config['DEFAULT_ROOM']
    cart = CartController.get_or_create(chat_id=xchat_id)

    data = json.loads(request.data)
    words = Items.filterWords(data['title'])
    if len(words) == 0:
        return json.dumps({'error': 'can not add product'}), 400, {'Content-Type': 'application/json; charset=utf-8'}

    data['title'] = " ".join(words)

    items = Item.objects(title=data['title'])
    if len(items) > 0:
        return json.dumps(items[0].as_api()), 200, {'Content-Type': 'application/json; charset=utf-8'}

    form = ItemForm.from_json(data)
    if form.validate():
        print 'creating product'
        data = form.data
        data.update({'cart_id': cart.id})
        item = Item(**data)
        item.save()
        return json.dumps(item.as_api()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return json.dumps({'error': 'can not add product'}), 400, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart/items', methods=['GET'])
def cart_items_list():
    xview = request.headers.get('X-Fridge-view', None)
    xchat_id = request.headers.get('X-Fridge-chat-id', None)
    if xchat_id is None or xchat_id == {} or xchat_id == "{}":
        xchat_id = app.config['DEFAULT_ROOM']
    cart = CartController.get_or_create(chat_id=xchat_id)
    items = Item.objects(cart_id=cart.id)

    if xview == 'ios':
        if cart.status == 'confirmed':
            data = ItemShopController.items_as_ios(items)
        else:
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
    xchat_id = request.headers.get('X-Fridge-chat-id', None)
    if xchat_id is None or xchat_id == {} or xchat_id == "{}":
        xchat_id = app.config['DEFAULT_ROOM']

    item = Item.objects.get(id=ObjectId(item_id))
    data = json.loads(request.data)
    form_data = item.to_form_data()
    for d in form_data:
        if d not in data:
            data.update({d: form_data[d]})
    form = ItemForm.from_json(data)
    if form.validate():
        item.title = data['title']
        item.shop_name = data['shop_name']
        item.price = data['price']
        item.count = data['count']
        item.save()
        Telegram.push(message=u"Список покупок уточнен, добавил %s" % item.shop_name, chat_id=xchat_id)
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
        item.magaz = a[3] or 'utkonos'
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
    xchat_id = request.headers.get('X-Fridge-chat-id', None)
    if xchat_id is None or xchat_id == {} or xchat_id == "{}":
        xchat_id = app.config['DEFAULT_ROOM']
    cart = CartController.get_or_create(chat_id=xchat_id)

    q = request.args.get('q', None)
    words = Items.filterWords(q)
    words = list(set(words))
    for w in words:

        items = Item.objects(title=w)
        if len(items) > 0:
            continue

        item = Item(title=w, cart_id=cart.id)
        item.save()
        Telegram.push(message=u"Добавил %s" % w, chat_id=xchat_id)
    return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart', methods=['POST'])
def cart_update():
    xchat_id = request.headers.get('X-Fridge-chat-id', None)
    if xchat_id is None or xchat_id == {} or xchat_id == "{}":
        xchat_id = app.config['DEFAULT_ROOM']
    cart = CartController.get_or_create(chat_id=xchat_id)

    cart.status = 'confirmed'
    cart.save()

    Telegram.push(message=u"Корзина сформирована", chat_id=xchat_id)
    Telegram.push(message=u"Оплатите покупки", chat_id=xchat_id)
    return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/cart', methods=['DELETE'])
def cart_delete():
    xchat_id = request.headers.get('X-Fridge-chat-id', None)
    if xchat_id is None or xchat_id == {} or xchat_id == "{}":
        xchat_id = app.config['DEFAULT_ROOM']
    cart = CartController.get_or_create(chat_id=xchat_id)

    items = Item.objects(cart_id=cart.id)
    for item in items:
        item.delete()
    Cart.objects.get(chat_id=xchat_id).delete()

    Telegram.push(message=u"Корзина удалена", chat_id=xchat_id)
    return json.dumps({}), 200, {'Content-Type': 'application/json; charset=utf-8'}
