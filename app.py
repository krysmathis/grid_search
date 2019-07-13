from flask import Flask, render_template, request, url_for, redirect, Response, flash, send_from_directory
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
SECRET_KEY = os.environ.get('HURR_SECRET_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def order_points(pts):
    
    pts = np.array(pts, dtype = "float32")
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
 
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
 
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
 
    # return the ordered coordinates
    return rect

def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
 
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
 
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
 
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
 
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
    # return the warped image
    return warped

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/images', methods=['POST','GET'])
def upload_file():
    
    if request.method == 'POST':
        print('POSTING...',len(request.files))
        print(request.args)
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('filename: ', filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # redirect(request.url,code=307)
            # return render_template('index.html',image_url='./static/images/shelftest.jpg')
            return Response(json.dumps('success'), status=200, mimetype='application/json')
            
    
    return render_template('index.html',image_url='./static/images/shelf2.jpg')



@app.route('/',methods=['GET','POST'])
def image_management():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            return render_template('index.html',image_url='./static/images/'+filename)
    
    # return render_template('index.html',image_url='./static/images/shelf2.jpg')
    return render_template('index.html',image_url='')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/annotate')
def annotate():
    return render_template('annotate.html')

@app.route('/upload',methods=['POST','GET'])
def upload():
    
    if request.method == 'POST':
        points = request.get_json()
        print(points)

    # now manipulate the image the way you want
        img = cv2.imread(points['image'])
        # img_slice = crop_img[pts[0][0]:pts[2][0],pts[3][0]:pts[1][0]]
        bbox = points['bbox']
        
        pts = [(p['x'],p['y']) for p in points['coords']]
        print('POG',points['pog'])
        selected_pog = points['pog']

        img_corrected = four_point_transform(img, pts)
        img_corrected = image_resize(img_corrected,height=800)
        cv2.imwrite('./static/images/tide_whatever.jpg',img_corrected)
        
        json_data = open(os.path.join('./static','planograms.json'),'r')
        planogram = json.load(json_data)
        
        pog = next((p for p in planogram if p['planogram'] == selected_pog), None)
        
        dict = pog['items']
        
        
        files = []
        # cut up the image
        for k,v in dict.items():
            cv2.imwrite('./static/images/' + k + '.jpg',img_corrected[int(dict[k][1]):int(dict[k][3]),int(dict[k][0]):int(dict[k][2])])
    #"apple_jacks_marshmallows": ["2", "2", "181", "127"]
            files.append('./static/images/' + k + '.jpg')
        return Response(json.dumps(files), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)