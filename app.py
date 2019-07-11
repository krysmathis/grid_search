from flask import Flask, render_template, request, Response
import json
import numpy as np
import cv2
import matplotlib.pyplot as plt


app = Flask(__name__)

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

@app.route('/')
def hello_world():
    return render_template('index.html',image_url='./static/images/shelf2.jpg')

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
        print(pts)


        img_corrected = four_point_transform(img, pts)
        img_corrected = image_resize(img_corrected,height=800)
        cv2.imwrite('./static/images/tide_whatever.jpg',img_corrected)

        dict = {
            "apple_jacks_marshmallows": ["2", "2", "181", "127"],
            "rice_krispies": ["183", "5", "458", "127"],
            "lucky_charms": ["462", "6", "550", "125"],
            "apple_jacks": ["4", "151", "178", "267"],
            "crispy_rice": ["181", "155", "356", "268"],
            "cv_frosted_flakes": ["365", "150", "542", "266"],
            "apple_jacks_family_size": ["2", "311", "160", "463"],
            "peanut_butter_crunch": ["162", "341", "249", "461"],
            "cinnamon_frosted_flakes": ["252", "343", "339", "459"],
            "frosted_flakes": ["344", "344", "523", "460"],
            "crunch_berries": ["4", "496", "172", "632"],
            "capn_crunch": ["175", "501", "363", "636"],
            "frosted_flakes_family_size": ["363", "490", "544", "631"],
            "giant_crunch_berries": ["7", "658", "232", "796"],
            "giant_capn_crunch": ["235", "655", "454", "796"],
            "pops": ["459", "660", "549", "796"]
        }

        files = []
        # cut up the image
        for k,v in dict.items():
            cv2.imwrite('./static/images/' + k + '.jpg',img_corrected[int(dict[k][1]):int(dict[k][3]),int(dict[k][0]):int(dict[k][2])])
    #"apple_jacks_marshmallows": ["2", "2", "181", "127"]
            files.append('./static/images/' + k + '.jpg')
        return Response(json.dumps(files), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)