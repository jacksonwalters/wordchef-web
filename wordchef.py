import logging
from lookup import nearest_words
from flask import Flask, render_template, flash, redirect
from forms import RecipeForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'

#if not run directly, enable gunicorn level logging
if __name__ != '__main__':
	#set loggers to gunicorn
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

@app.route("/", methods=['GET','POST'])
def recipe():
	form = RecipeForm()
	if form.validate_on_submit():

		#retrieve proportion data from form. 1 if (optionally) empty
		amount1 = (1 if form.amount1.data == None else form.amount1.data)
		amount2 = (1 if form.amount2.data == None else form.amount2.data)
		amount3 = (1 if form.amount3.data == None else form.amount3.data)
		amounts = [amount1,amount2,amount3]

		#retrieve word data from form. ""->" " if (optionally) empty
		word1 = (" " if form.word1.data == "" else form.word1.data)
		word2 = (" " if form.word2.data == "" else form.word2.data)
		word3 = (" " if form.word3.data == "" else form.word3.data)
		words = [word1,word2,amount3]

		#look up synonyms from vector sum
		result = ','.join(nearest_words(amounts,words))

		#flash the result
		flash('{}*{}+{}*{}+{}*{}~[{}]'.format(amount1,word1,amount2,word2,amount3,word3,result))
		return redirect('/')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
