import spacy
from flask import Flask, render_template, flash, redirect
from forms import RecipeForm
app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'
nlp = spacy.load('en_core_web_sm')

@app.route("/wordchef/", methods=['GET','POST'])
def recipe():
	form = RecipeForm()
	if form.validate_on_submit():
		#retrieve words
		word1 = form.word1.data
		word2 = form.word2.data
		#use spacy to get word vectors
		vec1 = nlp(form.word1.data).vector
		vec2 = nlp(form.word2.data).vector
		#add the vectors
		vec_sum = vec1 + vec2
		#look up synonym from vector sum
		#for now, just return sum as string
		sum_word = ','.join(vec_sum.astype(str))
		flash('{}+{}={}'.format(word1, word2, sum_word))
		return redirect('/wordchef')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
