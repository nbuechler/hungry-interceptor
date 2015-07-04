from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

#Form
class DefaultForm(Form):
    fieldA = StringField('fieldA', validators=[DataRequired()])