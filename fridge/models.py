# coding=utf-8
from collections import defaultdict

from mongoengine import Document, StringField, FloatField, IntField, ObjectIdField


class Item(Document):
    title = StringField(required=True)
    shop_name = StringField()
    price = FloatField()
    count = IntField()
    magaz = StringField()
    cart_id = ObjectIdField()
    state = StringField(default="{}")

    def __init__(self, *args, **values):
        self._id = None
        super(Item, self).__init__(*args, **values)

    def as_api(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'shop_name': self.shop_name,
            'price': self.price,
            'count': self.count
        }

    def to_form_data(self):
        return {
            'title': self.title,
            'shop_name': self.shop_name,
            'price': self.price,
            'count': self.count
        }


class Cart(Document):
    chat_id = StringField()
    status = StringField()


class CartController(object):
    @staticmethod
    def get_or_create(chat_id):
        carts = Cart.objects(chat_id=chat_id)
        if len(carts) == 0:
            cart = Cart(chat_id=chat_id)
            cart.save()
        else:
            cart = carts.first()
        return cart


class ItemController(object):
    @staticmethod
    def items_as_dict(items):
        return [i.as_api() for i in items]

    @staticmethod
    def items_as_ios(items):
        price_list = [
            {
                "@type": "PriceListPosition",
                "id": str(item.id),
                "price": item.price * 100 if item.price else None,
                # "img": "milk.png",
                "description": item.shop_name,
                "shop_name": item.shop_name,
                "count": item.count,
                "currency":
                    {
                        "@type": "CurrencyObject",
                        "name": "RUR",
                        "readable_name": u"Российский рубль",
                        "minor_units": 100
                    },
                "short_description": item.title,
                "title": item.title
            } for item in items
            ]
        return {
            "@type": "ProductListCardObject",
            "id": "unique_id_1234",
            "type": "product_list_raw",
            "score": 100500,
            "price_list": price_list
        }


class ItemShopController(object):
    @staticmethod
    def items_as_dict(items):
        item_by_shop = defaultdict(list)
        for item in items:
            item_by_shop[item.magaz].append(item)
        return item_by_shop

    @staticmethod
    def items_as_ios(items):
        storeItems = []
        items = filter(lambda x: x.magaz is not None, items)
        if len(items) > 0:
            item_by_shop = defaultdict(list)
            for item in items:
                item_by_shop[item.magaz].append(item)
            for shop in item_by_shop.keys():
                price_list = []
                for item in item_by_shop[shop]:
                    price_list.append({
                        "@type": "PriceListPosition",
                        "id": str(item.id),
                        "price": item.price * 100 if item.price else None,
                        # "img": "milk.png",
                        "description": item.shop_name,
                        "shop_name": item.shop_name,
                        "count": item.count,
                        "currency":
                            {
                                "@type": "CurrencyObject",
                                "name": "RUR",
                                "readable_name": u"Российский рубль",
                                "minor_units": 100
                            },
                        "short_description": item.title,
                        "title": item.title
                    })
                storeItems.append({
                        "storeId": shop,
                        "storeName": shop,
                        "price_list": price_list
                    })
        return {
            "@tfype": "ProductListCardObject",
            "id": "unique_id_1234",
            "type": "product_list_formed",
            "score": 100500,
            "storeItems": storeItems
        }
