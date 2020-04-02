from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import NumberRange, Optional, Length

class RecipeForm(FlaskForm):
	word1 = StringField('word1', render_kw={"placeholder": "flour"}, validators=[Optional(),Length(max=100,message="That's a pretty big meatball, buddy.")])
	amount1 = FloatField('amount1', render_kw={"placeholder": "1"}, validators=[Optional(),NumberRange(min=-100.0,max=100.0,message="That's a little spicy, pal.")])
	word2 = StringField('word2', render_kw={"placeholder": "egg"}, validators=[Optional(),Length(max=100,message="That's a lotta parm, sport.")])
	amount2 = FloatField('amount2', render_kw={"placeholder": "2.5"}, validators=[Optional(),NumberRange(min=-100.0,max=100.0,message="Easy with the olive oil, friend.")])
	submit = SubmitField('Cook!')
