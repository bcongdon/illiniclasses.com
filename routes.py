from flask import Flask, render_template, request
from search_bar import SearchBar

app = Flask(__name__)

app.secret_key = 'development-key'
@app.route('/', methods=['GET', 'POST'])
def index():
	form = SearchBar()
	if request.method == 'POST':
		return "Success"
	elif request.method == 'GET':
		return render_template('index.html', form=form)
		"""
		TODO:
		1. Check to see if course exists
		2. If yes, render_template to that route using a GET request
		3. If not, reload the page, pop-up an error message
		"""

if __name__ == '__main__':
  app.run(debug=True)