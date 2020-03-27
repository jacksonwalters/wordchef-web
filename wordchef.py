from flask import Flask, render_template, flash, redirect
from forms import RecipeForm
app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'

@app.route("/wordchef/", methods=['GET','POST'])
def recipe():
	form = RecipeForm()
	if form.validate_on_submit():
		flash('word1={}, word2={}'.format(form.word1.data, form.word2.data))
		return redirect('/wordchef')
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
