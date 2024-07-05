# -*- coding: utf-8 -*-
"""ParkingSpotClassifier.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GHQ0n5zWfoy2fdO6Wb8VuyPgOiYRdy8i
"""

import cv2
import numpy as np
import pandas as pd
import os
import datetime
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as img
from scipy.cluster.vq import whiten, kmeans
model_weights_path = './static/models/spots/best.onnx'

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

def parking(image_path,current_date, input_width, input_height, offset, confidence, class_score):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (640, 640), interpolation = cv2.INTER_LINEAR)
    net = cv2.dnn.readNetFromONNX(model_weights_path)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    # Check if the image was loaded successfully
    if img is None:
        print(f"Error: Unable to load image at path: {image_path}")
        return
    image = img.copy()
    row, col, d = image.shape

    max_rc = max(row, col)
    input_image = np.zeros((max_rc, max_rc, 3), dtype = np.uint8)
    input_image[0:row, 0:col] = image

    blob = cv2.dnn.blobFromImage(input_image, 1 / 255, (input_width, input_height), swapRB = True, crop = False)
    net.setInput(blob)
    preds = net.forward()
    detections = preds[0]

    centering_gap = offset

    empty, empty_boxes = bounding_box(input_image, detections, 5, confidence, input_width, input_height, class_score)
    occupied, occupied_boxes = bounding_box(input_image, detections, 6, confidence, input_width, input_height, class_score)
    output_full_image_path = f'./static/predict/SPOTS/{current_date}/output.jpg'
    output_full_image_path =os.path.join(PREDICT_PATH_SPOTS, current_date, 'output.jpg')
    output_full_image_path_xampp =os.path.join(XAMPP_PREDICT_PATH_SPOTS, current_date, 'output.jpg')
    # Create the "currentdate" folder if it doesn't exist
    folder_path = os.path.dirname(output_full_image_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
      # Create the "currentdate" folder if it doesn't exist
    folder_path = os.path.dirname(output_full_image_path_xampp)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    x_empty, y_empty, w_empty, h_empty = draw_bounding_boxes(image, output_full_image_path,output_full_image_path_xampp, empty, empty_boxes, centering_gap, (255, 0, 0))
    x_occupied, y_occupied, w_occupied, h_occupied = draw_bounding_boxes(image, output_full_image_path,output_full_image_path_xampp, occupied, occupied_boxes, centering_gap, (0, 255, 0))

    df_empty = pd.DataFrame(columns = ['index', 'X', 'Y', 'W', 'H', 'Status', 'Color'])
    df_occupied = pd.DataFrame(columns = ['index', 'X', 'Y', 'W', 'H', 'Status', 'Color'])

    df_empty['X'], df_empty['Y'], df_empty['W'], df_empty['H'], df_empty['Status'] =  x_empty, y_empty, w_empty, h_empty, 'E'
    df_occupied['X'], df_occupied['Y'], df_occupied['W'], df_occupied['H'], df_occupied['Status'] =  x_occupied, y_occupied, w_occupied, h_occupied , 'F'

    ranked_y = rank_numbers(y_empty + y_occupied)
    ranked_x = rank_numbers(x_empty + x_occupied)

    df_full = pd.concat([df_empty, df_occupied])
    df_full['Y_rank'] = ranked_y
    df_full['X_rank'] = ranked_x

    df_full = df_full.sort_values(['Y_rank', 'X_rank'])
    df_full['Spot Number'] = [x + 1 for x in list(range(df_full.shape[0]))]

    lst = []
    # current_date = datetime.datetime.now().strftime('%Y-%m-%d-%S')
    for i in range(len(x_occupied)):
        string = f"./static/roi/SPOTS/{current_date}/test/{i}.jpg"
        string = os.path.join(ROI_PATH_SPOTS, current_date, 'output',f"{i}.jpg")
        string_Xampp = os.path.join(XAMPP_ROI_PATH_SPOTS, current_date, 'output',f"{i}.jpg")

        # Create the "currentdate" folder if it doesn't exist
        folder_path = os.path.dirname(string)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # Create the "currentdate" folder if it doesn't exist
        folder_path = os.path.dirname(string_Xampp)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        cv2.imwrite(string, img[y_occupied[i] - centering_gap: y_occupied[i] + h_occupied[i] - centering_gap, x_occupied[i] : x_occupied[i] + w_occupied[i]])
        cv2.imwrite(string_Xampp, img[y_occupied[i] - centering_gap: y_occupied[i] + h_occupied[i] - centering_gap, x_occupied[i] : x_occupied[i] + w_occupied[i]])
    
    for i in range(len(x_occupied)):
        input_image_path = os.path.join(ROI_PATH_SPOTS, current_date, 'output',f"{i}.jpg")

        output_image_path = os.path.join(ROI_PATH_SPOTS, current_date, 'output',f"_({i}).jpg")
        output_image_path_xampp = os.path.join(XAMPP_ROI_PATH_SPOTS, current_date, 'output',f"_({i}).jpg")
        new_width = w_occupied[i] * 10
        new_height = h_occupied[i] * 10

        resize_image(input_image_path, output_image_path,output_image_path_xampp, new_width, new_height)

        color = car_color(output_image_path)
        lst.append(color)

    lst = [str(x) for x in lst]
    df_full.loc[df_full['Status'] == 'F', 'Color'] = lst
    # current_date = datetime.datetime.now().strftime('%Y-%m-%d-%S')
    csv_output_path = f'./static/predict/SPOTS/{current_date}/Parking Spots Details.csv'
    csv_output_path = os.path.join(PREDICT_PATH_SPOTS, current_date, 'Parking Spots Details.csv')
    csv_output_path_xampp = os.path.join(XAMPP_PREDICT_PATH_SPOTS, current_date, 'Parking Spots Details.csv')

    # Create the "currentdate" folder if it doesn't exist
    folder_path = os.path.dirname(csv_output_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Create the "currentdate" folder if it doesn't exist
    folder_path = os.path.dirname(csv_output_path_xampp)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    df_full.to_csv(csv_output_path, index=False)
    df_full.to_csv(csv_output_path_xampp, index=False)
    spot_status = {}

    for i, row in df_full.iterrows():
        spot_number = int(row['Spot Number'])
        status = row['Status']
        if status == 'F':
            color = row['Color']
            spot_status[spot_number] = {'Status': status, 'Color': color}
        else:
            spot_status[spot_number] = {'Status': status}
    return spot_status
def bounding_box(input_image, detections, spot_class, confidence_thresh, input_width, input_height, score):
    boxes = []
    confidences = []

    image_w, image_h = input_image.shape[:2]
    x_factor = image_w / input_width
    y_factor = image_h / input_height

    for i in range(len(detections)):
        row = detections[i]
        confidence = row[4]
        if confidence > confidence_thresh:
            class_score = row[spot_class]
            if class_score > score:
                cx, cy, w, h = row[0:4]

                left = int((cx - 0.5 * w) * x_factor)
                top = int((cy - 0.5) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])

                confidences.append(confidence)
                boxes.append(box)

    boxes_np = np.array(boxes).tolist()
    confidences_np = np.array(confidences).tolist()

    index = cv2.dnn.NMSBoxes(boxes_np, confidences_np, score, confidence_thresh)

    return index, boxes_np

def draw_bounding_boxes(image, out_img_path,xampp_out_img_path, class_spot, boxes_np, centering_gap, rgb):
    x_list = []
    y_list = []
    w_list = []
    h_list = []

    for ind in class_spot:
        x, y, w, h = boxes_np[ind]
        x_list.append(x)
        y_list.append(y)
        w_list.append(w)
        h_list.append(h)

        cv2.rectangle(image, (x, y - centering_gap), (x + w, y + h - centering_gap), rgb, 1)

    cv2.imwrite(out_img_path, image)
    cv2.imwrite(xampp_out_img_path, image)


    return x_list, y_list, w_list, h_list

def rank_numbers(unsorted_numbers):
    # Sort the original list
    sorted_numbers = sorted(unsorted_numbers)

    # Create a dictionary to store the rank of each number
    ranks = {}
    rank = 1
    for num in sorted_numbers:
        # If the number is not already in the dictionary, add it with its rank
        if num not in ranks:
            ranks[num] = rank
            rank += 1

    # Create a list of ranks corresponding to the original unsorted numbers
    ranked_list = [ranks[num] for num in unsorted_numbers]

    return ranked_list

def resize_image(input_image_path, output_image_path,output_image_path_xampp, new_width, new_height):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    resized_image.save(output_image_path)
    resized_image.save(output_image_path_xampp)

# def car_color(car_path):
    # car_image = img.imread(car_path)

    # r, g, b = [], [], []

    # for row in car_image:
    #     for temp_r, temp_g, temp_b in row:
    #         r.append(temp_r)
    #         g.append(temp_g)
    #         b.append(temp_b)

    # colors_df = pd.DataFrame({'red': r, 'blue': b, 'green': g,
    #                           'scaled_red': whiten(r), 'scaled_blue': whiten(b), 'scaled_green': whiten(g)})

    # r_std, g_std, b_std = colors_df[['red', 'green', 'blue']].std()

    # colors = []

    # n_cluster = 2
    # cluster_centers, _ = kmeans(colors_df[['scaled_red', 'scaled_blue', 'scaled_green']], n_cluster)

    # for cluster_center in cluster_centers:
    #     scaled_r, scaled_g, scaled_b = cluster_center
    #     colors.append((scaled_r * r_std / 255, scaled_g * g_std / 255, scaled_b * b_std / 255))

    # colors2 = np.array(colors)

    # has_one = np.any(colors2 > 1, axis=1)

    # for i, row_has_one in enumerate(has_one):
    #     if row_has_one:
    #         maxi = np.max(colors2, axis = 1).reshape(-1, 1)
    #         colors2[i] = colors2[i] * (255 / maxi[i])
    #     else:
    #         colors2[i] = colors2[i] * 255

    # for i in range(0, n_cluster):
    #     colors[i] = colors2[i].astype('int').tolist()

    # return list(colors)

    # # plt.imshow(car_image)
    # # plt.show()

    # # plt.imshow([colors])
    # # plt.show()
def car_color(car_path):
    car_image = img.imread(car_path)

    # Flatten the image array and separate the color channels
    pixels = car_image.reshape(-1, 3)
    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]

    # Create a DataFrame and whiten the color values
    colors_df = pd.DataFrame({'red': r, 'blue': b, 'green': g})
    colors_df['scaled_red'] = whiten(r)
    colors_df['scaled_blue'] = whiten(b)
    colors_df['scaled_green'] = whiten(g)

    r_std, g_std, b_std = colors_df[['red', 'green', 'blue']].std()

    # Perform k-means clustering
    n_cluster = 2
    cluster_centers, _ = kmeans(colors_df[['scaled_red', 'scaled_blue', 'scaled_green']], n_cluster)

    # Convert scaled cluster centers back to original color values
    colors = (cluster_centers * [r_std, g_std, b_std] / 255).tolist()
    colors = np.clip(colors, 0, 1) * 255
    colors = np.array(colors).astype(int).tolist()

    return colors


if __name__ == '__main__':
    # Example usage
    current_directory = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_directory, 'example.jpg')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    model_weights_path = os.path.join(current_directory, 'best.onnx')

    print(parking(
        image_path,
        current_date,
        640,
        640,
        10,
        0.5,
        0.5
    ))






# parking('/content/Untitled.jpeg',
#         'img_w_boxes2.jpg',
#         '/content/best.onnx',
#         640,
#         640,
#         20,
#         0.3,
#         0.1)

