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
	#md requires server w/ 4gb RAM, lg requires 8gb
	app.logger.info('loading nlp...')
	#nlp=spacy.load("en_core_web_md")
	nlp=spacy.load("en_core_web_lg")
	#prob controls number of queries to search. {-15:32k, -16:50k, -17:77k, -18:147k, -19:183k, -20:563k}
	queries = [w for w in nlp.vocab if w.is_lower and w.prob >= -16 and w.has_vector]
	app.logger.info('finished loading nlp.')

@app.route("/wordchef/", methods=['GET','POST'])
def recipe():
	form = RecipeForm()
	if form.validate_on_submit():

		#retrieve word data from form
		word1 = form.word1.data
		word2 = form.word2.data

		#retrieve proportion data from form. 1 if (optionally) empty
		amount1 = (1 if form.amount1.data == None else form.amount1.data)
		amount2 = (1 if form.amount2.data == None else form.amount2.data)

		#use spacy to get tokens
		token1 = [token for token in nlp(word1)][0]
		token2 = [token for token in nlp(word2)][0]

		#add the word vectors
		vec_sum = amount1*token1.vector + amount2*token2.vector

		#look up synonym from vector sum
		sum_word = ','.join(sim_words_from_vec(queries,vec_sum))

		#flash the result
		flash('{}*{}+{}*{}~[{}]'.format(amount1,word1,amount2,word2,sum_word))
		return redirect('/wordchef')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
