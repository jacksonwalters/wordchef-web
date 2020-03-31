from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class RecipeForm(FlaskForm):
	word1 = StringField('word1', validators=[DataRequired()])
	amount1 = FloatField('amount1', validators=[NumberRange(min=0.0,max=100.0)])
	word2 = StringField('word2', validators=[DataRequired()])
	amount2 = FloatField('amount2', validators=[NumberRange(min=0.0,max=100.0)])
	submit = SubmitField('Cook!')
