from flask import Flask, request, render_template, session, redirect, url_for
# Assuming your prediction logic is in a file named 'restaurant_predictor.py'
from AICalls import predict_best_restaurants
import os
import dotenv

dotenv.load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["flask-secret-key"]


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'past_searches' not in session:
        session['past_searches'] = []

    if request.method == 'POST':
        dining_preference = request.form['dining_preference']
        predictions = predict_best_restaurants(dining_preference)

        if isinstance(predictions, str):
            predictions = [p.strip() for p in predictions.split('\n\n')]

        session['past_searches'].append({'query': dining_preference, 'results': predictions})
        session['past_searches'] = session['past_searches'][-10:]#  Limit the number of stored searches (optional)
        return (render_template('index.html', query=dining_preference, predictions=predictions, past_searches=session['past_searches'][::-1]))
    else:
        # Enumerate the past_searches in the Flask code
        return render_template('index.html',past_searches=session['past_searches'][::-1], predictions=[], query="")



@app.route('/search/<int:search_index>')
def show_past_search(search_index):
    if 'past_searches' in session and 0 <= search_index < len(session['past_searches']):
        past_search = session['past_searches'][search_index]
        return render_template('index.html', query=past_search['query'], predictions=past_search['results'], past_searches=session['past_searches'][::-1])
    else:
        return redirect(url_for('index'))  # Redirect to homepage if index is invalid

if __name__ == '__main__':
    app.run(debug=True)

