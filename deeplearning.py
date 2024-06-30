import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
# from PIL import Image, ImageDraw, ImageFont
# import arabic_reshaper
# from bidi.algorithm import get_display
import easyocr

BASE_PATH = os.getcwd()
UPLOAD_PATH_NPR = os.path.join(BASE_PATH, 'static', 'upload', 'NPR')
UPLOAD_PATH_SPOTS = os.path.join(BASE_PATH, 'static', 'upload', 'SPOTS')
ROI_PATH_NPR = os.path.join(BASE_PATH, 'static', 'roi', 'NPR')
ROI_PATH_SPOTS = os.path.join(BASE_PATH, 'static', 'roi', 'SPOTS')
PREDICT_PATH_NPR = os.path.join(BASE_PATH, 'static', 'predict', 'NPR')
PREDICT_PATH_SPOTS = os.path.join(BASE_PATH, 'static', 'predict', 'SPOTS')

# Define the XAMPP htdocs directory paths
# Adjust the path based on your XAMPP installation directory
if os.name == 'nt':  # Windows
    XAMPP_HTDOCS_PATH = 'C:/xampp/htdocs'
else:  # Unix-based (Linux/MacOS)
    XAMPP_HTDOCS_PATH = '/opt/lampp/htdocs'

XAMPP_UPLOAD_PATH_NPR = os.path.join(XAMPP_HTDOCS_PATH,'my-api', 'AI', 'upload', 'NPR')
XAMPP_UPLOAD_PATH_SPOTS = os.path.join(XAMPP_HTDOCS_PATH,'my-api', 'AI', 'upload', 'SPOTS')
XAMPP_ROI_PATH_NPR = os.path.join(XAMPP_HTDOCS_PATH,'my-api', 'AI', 'roi', 'NPR')
XAMPP_ROI_PATH_SPOTS = os.path.join(XAMPP_HTDOCS_PATH,'my-api', 'AI', 'roi', 'SPOTS')
XAMPP_PREDICT_PATH_NPR = os.path.join(XAMPP_HTDOCS_PATH,'my-api', 'AI', 'predict', 'NPR')
XAMPP_PREDICT_PATH_SPOTS = os.path.join(XAMPP_HTDOCS_PATH,'my-api', 'AI', 'predict', 'SPOTS')

# Ensure all directories exist
directories = [
    UPLOAD_PATH_NPR, UPLOAD_PATH_SPOTS, ROI_PATH_NPR, ROI_PATH_SPOTS,
    PREDICT_PATH_NPR, PREDICT_PATH_SPOTS, XAMPP_UPLOAD_PATH_NPR,
    XAMPP_UPLOAD_PATH_SPOTS, XAMPP_ROI_PATH_NPR, XAMPP_ROI_PATH_SPOTS,
    XAMPP_PREDICT_PATH_NPR, XAMPP_PREDICT_PATH_SPOTS
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)

# model = tf.keras.models.load_model('./static/models/object_detection.h5')

""" 
def object_detection(path,filename):
    # read image
    image = load_img(path) # PIL object
    image = np.array(image,dtype=np.uint8) # 8 bit array (0,255)
    image1 = load_img(path,target_size=(224,224))
    # data preprocessing
    image_arr_224 = img_to_array(image1)/255.0  # convert into array and get the normalized output
    h,w,d = image.shape
    test_arr = image_arr_224.reshape(1,224,224,3)
    # make predictions
    coords = model.predict(test_arr)
    # denormalize the values
    denorm = np.array([w,w,h,h])
    coords = coords * denorm
    coords = coords.astype(np.int32)
    # draw bounding on top the image
    xmin, xmax,ymin,ymax = coords[0]
    pt1 =(xmin,ymin)
    pt2 =(xmax,ymax)
    print(pt1, pt2)
    cv2.rectangle(image,pt1,pt2,(0,255,0),3)
    # convert into bgr
    image_bgr = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
    cv2.imwrite('./static/predict/{}'.format(filename),image_bgr)
    return coords """
# settings
INPUT_WIDTH =  640
INPUT_HEIGHT = 640
net = cv2.dnn.readNetFromONNX('./static/models/best.onnx')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
def get_detections(img,net):
    # CONVERT IMAGE TO YOLO FORMAT
    image = img.copy()
    row, col, d = image.shape

    max_rc = max(row,col)
    input_image = np.zeros((max_rc,max_rc,3),dtype=np.uint8)
    input_image[0:row,0:col] = image

    # GET PREDICTION FROM YOLO MODEL
    blob = cv2.dnn.blobFromImage(input_image,1/255,(INPUT_WIDTH,INPUT_HEIGHT),swapRB=True,crop=False)
    net.setInput(blob)
    preds = net.forward()
    detections = preds[0]
    
    return input_image, detections

def non_maximum_supression(input_image,detections):
    # FILTER DETECTIONS BASED ON CONFIDENCE AND PROBABILIY SCORE
    # center x, center y, w , h, conf, proba
    boxes = []
    confidences = []

    image_w, image_h = input_image.shape[:2]
    x_factor = image_w/INPUT_WIDTH
    y_factor = image_h/INPUT_HEIGHT

    for i in range(len(detections)):
        row = detections[i]
        confidence = row[4] # confidence of detecting license plate
        if confidence > 0.4:
            class_score = row[5] # probability score of license plate
            if class_score > 0.25:
                cx, cy , w, h = row[0:4]

                left = int((cx - 0.5*w)*x_factor)
                top = int((cy-0.5*h)*y_factor)
                width = int(w*x_factor)
                height = int(h*y_factor)
                box = np.array([left,top,width,height])

                confidences.append(confidence)
                boxes.append(box)

    # clean
    boxes_np = np.array(boxes).tolist()
    confidences_np = np.array(confidences).tolist()
    if boxes_np == []:
        return None,None,0
    # NMS
    index = cv2.dnn.NMSBoxes(boxes_np,confidences_np,0.25,0.45).flatten()
    
    return boxes_np, confidences_np, index

def drawings(image,boxes_np,confidences_np,index,filename):
    # drawings
    for ind in index:
        x,y,w,h =  boxes_np[ind]
        bb_conf = confidences_np[ind]
        conf_text = 'plate: {:.0f}%'.format(bb_conf*100)
#        license_text = extract_text(image,boxes_np[ind])


        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
#         cv2.rectangle(image,(x,y-30),(x+w,y),(0,255,0),-1)
#         cv2.rectangle(image,(x,y+h),(x+w,y+h+30),(0,255,0),-1)


#         cv2.putText(image,conf_text,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),1)
#         cv2.putText(image,license_text,(x,y+h+27),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),1)
    cv2.imwrite(PREDICT_PATH_NPR+"/"+filename,image)
    cv2.imwrite(XAMPP_PREDICT_PATH_NPR+"/"+filename,image)
    return image
def yolo_predictions(img,net,filename):
    ## step-1: detections
    input_image, detections = get_detections(img,net)
    
    ## step-2: NMS
    boxes_np, confidences_np, index = non_maximum_supression(input_image, detections)
    if boxes_np == None:
        return None
    ## step-3: Drawings
    result_img = drawings(img,boxes_np,confidences_np,index,filename)
    return  boxes_np[index[0]]
def OCR(path,filename):
    reader = easyocr.Reader(['ar'])
    img = cv2.imread(path)
    
    bbox = yolo_predictions(img,net,filename)
    if bbox == None:
        return None
    x,y,w,h = bbox
    roi = img[y:y+h, x:x+w]
    # plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    # plt.axis('off')  # Turn off axis numbers and ticks
    # plt.show()

    cv2.imwrite(ROI_PATH_NPR+"/"+filename,roi)
    cv2.imwrite(XAMPP_ROI_PATH_NPR+"/"+filename,roi)

    #roi_bgr = cv2.cvtColor(roi,cv2.COLOR_RGB2BGR)
    #cv2.imwrite('./static/roi/{}'.format(filename),roi_bgr)

    denoised_image = cv2.fastNlMeansDenoisingColored(roi, None, 10, 10, 7, 21)
    
    resize_test_license_plate = cv2.resize( 
    denoised_image, None, fx = 2, fy = 2,  
    interpolation = cv2.INTER_CUBIC)
    
    grayscale_resize_test_license_plate = cv2.cvtColor( 
    resize_test_license_plate, cv2.COLOR_BGR2GRAY) 
    
    gaussian_blur_license_plate = cv2.GaussianBlur( 
    grayscale_resize_test_license_plate, (5, 5), 0) 
    
    _, thresholded_image = cv2.threshold(gaussian_blur_license_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU )
#     kernel = np.ones((5,5),np.uint8)
#     dilated_image = cv2.dilate(thresholded_image, kernel, iterations = 1)
#     eroded_image = cv2.erode(dilated_image, kernel, iterations = 1)
    
    
    roi = thresholded_image
    if 0 in roi.shape:
        print("no roi")
        return ''
    
    else:
        print("roi found")
        text = reader.readtext(roi)  # Perform OCR on the cropped image
        
        return text
