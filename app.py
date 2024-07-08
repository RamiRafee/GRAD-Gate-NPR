from flask import Flask, render_template, request, jsonify
import os 
import tensorflow.keras.backend as K
from deeplearning import OCR
from CustomOCR import customocr
from parkingspotclassifier import parking
from DBinterface import check_car_existence, check_premium_status, update_SPOTS, append_to_file
from datetime import datetime, timedelta

# webserver gateway interface
app = Flask(__name__)

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

def separate_letters(input_string):
    result = ''
    for i, char in enumerate(input_string):
        if char.isalnum() or (i != 0 and char != ' '):
            result += char + ' '
    return result.strip()

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        if 'image_name_NPR' in request.files:
            current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            upload_file = request.files['image_name_NPR']
            original_filename = upload_file.filename
            base_filename = current_date
            extension = os.path.splitext(original_filename)[1]
            filename = base_filename + extension


            # Read the file content
            file_content = upload_file.read()

            # Save the file in the Flask app directory
            flask_path = os.path.join(UPLOAD_PATH_NPR, filename)
            with open(flask_path, 'wb') as f:
                f.write(file_content)

            # Save the file in the XAMPP htdocs directory
            xampp_path = os.path.join(XAMPP_UPLOAD_PATH_NPR, filename)
            with open(xampp_path, 'wb') as f:
                f.write(file_content)


            easyOCRtext = OCR(flask_path, filename)
            if easyOCRtext == None:
                return render_template('index.html', NPR=True, upload_image=filename, easyOCRtext="NO ROI FOUND!",customOCRtext="NO ROI FOUND!")
            roiPath = ROI_PATH_NPR+"/"+current_date+".jpg"
            CustomOCRtext = customocr(roiPath)
            CustomOCRtext = separate_letters(CustomOCRtext)

            # Create a new filename with CarNum appended
            new_filename = f"{base_filename}_{CustomOCRtext}{extension}"
            flask_path = os.path.join(PREDICT_PATH_NPR, filename)
            new_flask_path = os.path.join(PREDICT_PATH_NPR, new_filename)
            xampp_path = os.path.join(XAMPP_PREDICT_PATH_NPR, filename)
            new_xampp_path = os.path.join(XAMPP_PREDICT_PATH_NPR, new_filename)
            
            # Rename the file in the Flask app directory
            os.rename(flask_path, new_flask_path)
            os.rename(xampp_path, new_xampp_path)
            

            return render_template('index.html', NPR=True, upload_image=filename ,predict_image = new_filename, easyOCRtext=easyOCRtext, customOCRtext=CustomOCRtext)
        elif 'image_name_SPOTS' in request.files:
            upload_file = request.files['image_name_SPOTS']

            current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            filename = current_date+".jpg"


            # Read the file content
            file_content = upload_file.read()

            # Save the file in the Flask app directory
            flask_path = os.path.join(UPLOAD_PATH_SPOTS, filename)
            with open(flask_path, 'wb') as f:
                f.write(file_content)

            # Save the file in the XAMPP htdocs directory
            xampp_path = os.path.join(XAMPP_UPLOAD_PATH_SPOTS, filename)
            with open(xampp_path, 'wb') as f:
                f.write(file_content)
            spots = parking(
                flask_path,
                current_date,
                640,
                640,
                40,
                0.35,
                0.25
            )

            
            return render_template('index.html', SPOTS=True, upload_image=filename, current_date=current_date, spots= spots)
    return render_template('index.html', upload=False)



@app.route('/upload_image_NPR', methods=['POST'])
def upload_image_NPR():
    if request.method == 'POST':
        current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        if 'image' not in request.files:
            return 'No file part'
        upload_file = request.files['image']
        if upload_file.filename == '':
            return 'No selected file'
        filename = current_date+".jpg"


        # Read the file content
        file_content = upload_file.read()

        # Save the file in the Flask app directory
        flask_path = os.path.join(UPLOAD_PATH_NPR, filename)
        with open(flask_path, 'wb') as f:
            f.write(file_content)

        # Save the file in the XAMPP htdocs directory
        xampp_path = os.path.join(XAMPP_UPLOAD_PATH_NPR, filename)
        with open(xampp_path, 'wb') as f:
            f.write(file_content)
        
        
        number_plate = OCR(flask_path, filename)
        if number_plate == None:
            return {'message':"False"}
        roiPath = ROI_PATH_NPR+"/"+current_date+".jpg"
        CustomOCRtext = customocr(roiPath)
        #CustomOCRtext = "ر ج ل 2 2 2"
        if CustomOCRtext == None:
            return {'message':"False"}
        CarNum = separate_letters(CustomOCRtext)
        append_to_file("./static/entered_car_num.txt",CarNum)
        if(check_car_existence(CarNum)):
            preimum_status = check_premium_status(CarNum)

            # Get the current date and time
            current_datetime = datetime.now()

            # Calculate the departure datetime (current datetime + 3 hours)
            departure = current_datetime + timedelta(hours=3)

            # Format the arrival and departure datetimes as strings
            arrival_str = current_datetime.strftime('%Y-%m-%d')
            departure_str = departure.strftime('%Y-%m-%d')
            position = 'A1'
            
            return {'message':"True",'Premium':preimum_status}

        else:
            return {'message':"False"}
        
@app.route('/upload_image_SPOTS', methods=['POST'])
def upload_image_SPOTS():
    
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'
        upload_file = request.files['image']
        if upload_file.filename == '':
            return 'No selected file'

        current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = current_date+".jpg"


        # Read the file content
        file_content = upload_file.read()

        # Save the file in the Flask app directory
        flask_path = os.path.join(UPLOAD_PATH_SPOTS, filename)
        with open(flask_path, 'wb') as f:
            f.write(file_content)

        # Save the file in the XAMPP htdocs directory
        xampp_path = os.path.join(XAMPP_UPLOAD_PATH_SPOTS, filename)
        with open(xampp_path, 'wb') as f:
            f.write(file_content)
        
        spots = parking(
            flask_path,
            current_date,
            640,
            640,
            40,
            0.35,
            0.25
        )
        #spots = {1: {'Status': 'E'}, 2: {'Status': 'F', 'Color': '[[56, 52, 56], [148, 141, 147]]'}, 3: {'Status': 'E'}, 4: {'Status': 'F', 'Color': '[[56, 52, 56], [148, 141, 147]]'}, 5: {'Status': 'E'}, 6: {'Status': 'E'}, 7: {'Status': 'E'}, 8: {'Status': 'E'}, 9: {'Status': 'E'}, 10: {'Status': 'E'}, 11: {'Status': 'E'}, 12: {'Status': 'E'}, 13: {'Status': 'F', 'Color': '[[186, 177, 207], [73, 56, 81]]'}, 14: {'Status': 'E'}, 15: {'Status': 'E'}, 16: {'Status': 'E'}, 17: {'Status': 'E'}, 18: {'Status': 'E'}, 19: {'Status': 'E'}, 20: {'Status': 'E'}, 21: {'Status': 'E'}, 22: {'Status': 'F', 'Color': '[[202, 200, 210], [74, 67, 75]]'}, 23: {'Status': 'E'}, 24: {'Status': 'E'}, 25: {'Status': 'E'}, 26: {'Status': 'E'}, 27: {'Status': 'E'}, 28: {'Status': 'E'}, 29: {'Status': 'E'}, 30: {'Status': 'E'}, 31: {'Status': 'E'}, 32: {'Status': 'F', 'Color': '[[205, 206, 212], [59, 56, 60]]'}, 33: {'Status': 'E'}, 34: {'Status': 'E'}, 35: {'Status': 'F', 'Color': '[[135, 108, 106], [80, 40, 40]]'}, 36: {'Status': 'E'}, 37: {'Status': 'F', 'Color': '[[88, 80, 87], [214, 209, 220]]'}, 38: {'Status': 'E'}, 39: {'Status': 'F', 'Color': '[[37, 30, 36], [90, 79, 84]]'}, 40: {'Status': 'E'}}
        update_status = update_SPOTS('standard_garage_info',spots,"./static/entered_car_num.txt")   
        return {"message":update_status}

        

if __name__ =="__main__":
    app.run(debug=True)