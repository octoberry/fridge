from wtforms import Form, StringField, IntegerField, validators
import wtforms_json
wtforms_json.init()


class ProductForm(Form):
    title = StringField(validators=[validators.required()])
    count = IntegerField()
