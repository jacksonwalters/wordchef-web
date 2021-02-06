import logging, pickle, numpy
from flask import Flask, render_template, flash, redirect
from forms import RecipeForm

#initialize flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'

#load word2vec dictionary from pickle file
with open('./vocab/dict.pkl','rb') as f:
	to_vec = pickle.load(f)
#load wordvector balltree from pickle file
with open('./vocab/balltree.pkl','rb') as f:
	tree = pickle.load(f)
#load vocab list from pickle file
with open('./vocab/vocab.pkl','rb') as f:
	vocab = pickle.load(f)

#form linear combination of wordvectors and lookup nearest words
def nearest_words(amounts,words):
	#get vectors for all words
	vecs=[]
	for word in words:
		try:
			vec = to_vec[word]
			vecs.append(vec)
		#if word is not in vocab, do not include
		except KeyError:
			vecs.append(numpy.zeros(300))

	#compute linear combination of user wordvectors
	assert len(vecs) == len(amounts)
	n = len(vecs)
	lin_comb = numpy.zeros(300)
	for i in range(n):
		lin_comb += amounts[i]*vecs[i]

	#perform nearest neighbor search of wordvector vocabulary
	dist, ind = tree.query([lin_comb],10)

	#lookup nearest words using indices from tree
	near_words = [vocab[i] for i in ind[0]]

	return near_words

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
		word1 = (" " if form.word1.data == "" else form.word1.data.strip().lower())
		word2 = (" " if form.word2.data == "" else form.word2.data.strip().lower())
		word3 = (" " if form.word3.data == "" else form.word3.data.strip().lower())
		words = [word1,word2,word3]

		#flash the input
		flash('{}*{}+{}*{}+{}*{}~'.format(amount1,word1,amount2,word2,amount3,word3),'input')

		#look up synonyms from vector sum
		result = ','.join(nearest_words(amounts,words))
		flash(result,'output')

		return redirect('/')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
else:
	#enable gunicorn level logging
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)
