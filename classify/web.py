import pickle
from flask import Flask, request
from sklearn_experiments import predict

app = Flask(__name__)

home_html = '''
    <style>
        * {
            font-family: Helvetica;
        }
    </style>
    <form action="/" method="POST">
        <input type="text" name="tweet" placeholder="tweet">
        <input type="submit">
    </form>
    <span id="result">
    </span>
'''

# https://github.com/Ranks/emojify.js

with open('trained_models/vectorizer', 'rb') as f:
    vectorizer = pickle.loads(f.read())

with open('trained_models/GaussianNB', 'rb') as f:
    classifier = pickle.loads(f.read())

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return home_html
    return str(predict(request.form['tweet'], vectorizer, classifier))

if __name__ == '__main__':
    app.run(debug=True)
