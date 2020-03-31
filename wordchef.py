import spacy
import logging
from flask import Flask, render_template, flash, redirect
from forms import RecipeForm
from similar import sim_words_from_vec

app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'

#if not run directly, enable gunicorn level logging
if __name__ != '__main__':
	#set loggers to gunicorn
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	#load natural language processing spacy
	app.logger.info('not running as __main__')
	app.logger.info('loading nlp...')

	#medium requires server w/ 4gb RAM, large requires 8gb
	#nlp=spacy.load("en_core_web_md")
	nlp=spacy.load("en_core_web_lg")

	app.logger.info('finished loading nlp.')

@app.route("/wordchef/", methods=['GET','POST'])
def recipe():
	app.logger.info('flask routed to /wordchef')
	form = RecipeForm()
	if form.validate_on_submit():

		app.logger.info('form validated')

		#retrieve word data from form
		word1 = form.word1.data
		word2 = form.word2.data

		#retrieve proportion data from form
		amount1 = form.amount1.data
		amount2 = form.amount2.data

		#use spacy to get tokens
		token1 = [token for token in nlp(word1)][0]
		token2 = [token for token in nlp(word2)][0]

		#add the word vectors
		vec_sum = amount1*token1.vector + amount2*token2.vector

		#look up synonym from vector sum
		sum_word = ','.join(sim_words_from_vec(nlp.vocab,vec_sum))

		#flash the result
		flash('{}*{}+{}*{}~[{}]'.format(amount1,word1,amount2,word2,sum_word))
		return redirect('/wordchef')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
	app.logger.info('running as __main__')
	app.run(host='0.0.0.0', debug=True)
