from flask import Flask, render_template, request, Response
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/coords',methods=['POST','GET'])
def coords():
    
    if request.method == 'POST':
        points = request.get_json()
        print(points)
        return Response(json.dumps(points), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)