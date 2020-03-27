from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class RecipeForm(FlaskForm):
	word1 = StringField('word1', validators=[DataRequired()])
	word2 = StringField('word2', validators=[DataRequired()])
	submit = SubmitField('Recipe')
