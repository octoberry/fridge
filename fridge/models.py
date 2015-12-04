# coding=utf-8
from mongoengine import Document, StringField, FloatField, IntField


class Item(Document):
    title = StringField(required=True)
    shop_name = StringField()
    price = FloatField()
    count = IntField()

    def __init__(self, *args, **values):
        self._id = None
        super(Item, self).__init__(*args, **values)


class ItemController(object):
    @staticmethod
    def items_as_ios(items):
        price_list = [
            {
                "@type": "PriceListPosition",
                "id": str(item.id),
                "price": item.price,
                # "img": "milk.png",
                "description": item.shop_name,
                "count": item.count,
                "currency":
                    {
                        "@type": "CurrencyObject",
                        "name": "RUR",
                        "readable_name": u"Российский рубль",
                        "minor_units": 100
                    },
                "short_description": item.title
            } for item in items
        ]
        return {
            "@type": "ProductListCardObject",
            "id": "unique_id_1234",
            "type": "product_list_raw",
            "score": 100500,
            "price_list": price_list
        }
