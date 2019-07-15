from flask import Flask, render_template, request, url_for, redirect, Response, flash, send_from_directory
from werkzeug.utils import secure_filename
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
# import boto3, botocore
import urllib
from datetime import datetime

# from io import BytesIO
# import imageio

UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# S3_BUCKET                 = os.environ.get("S3_BUCKET_NAME")
# S3_KEY                    = os.environ.get("S3_ACCESS_KEY")
# S3_SECRET                 = os.environ.get("S3_SECRET_ACCESS_KEY")
# S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000

DEV_LOCAL                 = True

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY


# s3 = boto3.client(
#    "s3",
#    aws_access_key_id=S3_KEY,
#    aws_secret_access_key=S3_SECRET
# )

# def upload_file_to_s3(file, bucket_name, acl="public-read"):
    
#     """
#     Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
#     """
#     try:

#         # s3_resource = boto3.resource('s3')
#         #my_bucket = s3.Bucket(S3_BUCKET)
#         #my_bucket.Object(file.filename).put(Body=file)

#         s3.upload_fileobj(
#             file,
#             bucket_name,
#             file.filename,
#             ExtraArgs={
#                 "ACL": acl,
#                 "ContentType": file.content_type
#             }
#         )

#     except Exception as e:
#         print("Something Happened: ", e)
#         return e

#     return "{}{}".format(S3_LOCATION, file.filename)


def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
 
	# return the image
	return image


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

# @app.route('/images', methods=['POST','GET'])
# def upload_file():
    
#     if request.method == 'POST':
#         print('POSTING...',len(request.files))
#         print(request.args)
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             print('no file part')
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         print(file.filename)
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
        
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             print('filename: ', filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
#             # redirect(request.url,code=307)
#             # return render_template('index.html',image_url='./static/images/shelftest.jpg')
#             return Response(json.dumps('success'), status=200, mimetype='application/json')
            
    
#     return render_template('index.html',image_url='./static/images/shelf2.jpg')


@app.route('/home',methods=['GET','POST'])
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
            file.filename = filename
            amazon_file = file

            if DEV_LOCAL == True: # using local files saving on s3 load
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('index.html',image_url='./static/images/'+filename, image_bucket='./static/images/')
            
            # uncomment the next two lines when usings s3
            # upload_results = upload_file_to_s3(file, S3_BUCKET)
            # image_url = str(upload_results)
            
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
            # print('AMAZON_PART:', str(upload_file_to_s3(file, S3_BUCKET)))
            # return render_template('index.html',image_url='./static/images/'+filename)
            return render_template('index.html',image_url=image_url,image_bucket='./static/images/')
    else:
        # return render_template('index.html',image_url='./static/images/shelf2.jpg')
        return render_template('index.html',image_url='',image_bucket='./static/images/')

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
        
        if DEV_LOCAL == False:
            url = points['image']
            img = url_to_image(url)
        else:
            img = cv2.imread(points['image'])

        bbox = points['bbox']
        
        pts = [(p['x'],p['y']) for p in points['coords']]
        print('POG',points['pog'])
        
        selected_pog = points['pog']
        json_data = open(os.path.join('./static','planograms.json'),'r')
        planogram = json.load(json_data)
        pog = next((p for p in planogram if p['planogram'] == selected_pog), None)
        
        pog_height = pog['height']
        img_corrected = four_point_transform(img, pts)
        img_corrected = image_resize(img_corrected,height=pog_height)
        
        cv2.imwrite('./static/images/tide_whatever.jpg',img_corrected)
        
        pog_items = pog['items']
        
        files = []

        ts = datetime.now().timestamp()
        # cut up the image
        for k,v in pog_items.items():
            
            sliced_image = img_corrected[int(pog_items[k][1]):int(pog_items[k][3]),int(pog_items[k][0]):int(pog_items[k][2])]
            
            # calc to check if it is within darkness threshold
            gray = cv2.cvtColor(sliced_image, cv2.COLOR_BGR2GRAY)
            light_threshold = 10
            is_light = 1 if np.mean(gray) > light_threshold else 0
            
            
            # delete if exists
            file_path = './static/images/slices/' + str(ts) + '__' + k + '.jpg'
            if os.path.exists(file_path):
                os.remove(file_path)

            cv2.imwrite(file_path,sliced_image)
            files.append({'path': file_path ,'is_light': is_light})
        
        return Response(json.dumps(files), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)