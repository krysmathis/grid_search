from flask import Flask, render_template, request, Response
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/upload',methods=['POST','GET'])
def upload():
    
    if request.method == 'POST':
        points = request.get_json()
        print(points)

    # now manipulate the image the way you want
        img = cv2.imread(points['image'])
        # img_slice = crop_img[pts[0][0]:pts[2][0],pts[3][0]:pts[1][0]]
        bbox = points['bbox']
        
        img = img[bbox[0]:bbox[1],bbox[2]:bbox[3]]
        cv2.imwrite('./static/images/tide_whatever.jpg',img)

        return Response(json.dumps(points), status=200, mimetype='application/json')
if __name__ == '__main__':
    app.run(debug=True)