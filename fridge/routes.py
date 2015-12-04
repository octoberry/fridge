# coding=utf-8
from flask import request

from fridge.app import app, state
from product.find import Beer


@app.route('/cart/items', methods=['POST'])
def cart_items():

    return '', 200


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
