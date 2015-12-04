from wtforms import Form, StringField, IntegerField, FloatField, validators
import wtforms_json
wtforms_json.init()


class ItemForm(Form):
    title = StringField(validators=[validators.required()])
    shop_name = StringField()
    price = FloatField()
    count = IntegerField()
