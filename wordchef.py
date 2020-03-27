from flask import Flask, render_template
from forms import RecipeForm
app = Flask(__name__)
app.config['SECRET_KEY'] = 'play-it-as-it-lays'

@app.route("/wordchef/", methods=['GET','POST'])
def recipe():
	form = RecipeForm()
	return render_template('recipe.html', title='word+chef', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
