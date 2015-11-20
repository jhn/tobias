from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)



@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/api/image',methods=['POST'])
def send_pic():
    return jsonify({'tasks': tasks})

if __name__ == "__main__":
    app.run(debug=True)
