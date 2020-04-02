from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class RecipeForm(FlaskForm):
	word1 = StringField('word1', validators=[DataRequired(message="Where's the flour?")])
	amount1 = FloatField('amount1', validators=[Optional(),NumberRange(min=0.0,max=100.0,message="That's a little spicy, pal.")])
	word2 = StringField('word2', validators=[DataRequired(message="Put an egg in there.")])
	amount2 = FloatField('amount2', validators=[Optional(),NumberRange(min=0.0,max=100.0,message="Woah, slow down champ.")])
	submit = SubmitField('Cook!')
