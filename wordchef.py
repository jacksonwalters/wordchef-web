import spacy
import logging
from flask import Flask, render_template, flash, redirect
from forms import RecipeForm
from similar import sim_words_from_vec

app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'

#if not run directly, enable gunicorn level logging
if __name__ != '__main__':
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)

	app.logger.info('not running as __main__')
	app.logger.info('loading nlp...')
	nlp=spacy.load("en_core_web_md")
	app.logger.info('finished loading nlp.')

@app.route("/wordchef/", methods=['GET','POST'])
def recipe():
	form = RecipeForm()
	if form.validate_on_submit():

		#retrieve words from form
		word1 = form.word1.data
		word2 = form.word2.data

		#use spacy to get tokens
		token1 = [token for token in nlp(word1)][0]
		token2 = [token for token in nlp(word2)][0]

		#add the word vectors
		vec_sum = token1.vector + token2.vector

		#look up synonym from vector sum
		sum_word = ','.join(sim_words_from_vec(nlp.vocab,vec_sum))

		#flash the result
		flash('{}+{}~[{}]'.format(word1, word2, sum_word))
		return redirect('/wordchef')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
	app.logger.info('running as __main__')
	app.run(host='0.0.0.0', debug=True)
