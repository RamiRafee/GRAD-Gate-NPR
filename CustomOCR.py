import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
import matplotlib.pyplot as plt

def customocr(image_path):
    char_list = ' شه045لذس2ط71قك83رجت6بثا9دضزوعظغىفنمخصح'

    # Load the model
    loaded_model = tf.keras.models.load_model('./static/models/OCR/OCR-CustomModel.h5')
    # Read and preprocess the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        img = cv2.resize(img, (128, 32))
    else :
        return None
    img = np.expand_dims(img, axis=2)
    img = np.expand_dims(img, axis=0)

    # Predict characters from the image
    prediction = loaded_model.predict(img)

    # Use CTC decoder to decode the predictions
    out = K.get_value(K.ctc_decode(prediction, input_length=np.ones(prediction.shape[0]) * prediction.shape[1], greedy=True)[0][0])

    # Decode the predictions into text
    predicted_text = ''
    for p in out:
        for p_idx in p:
            if int(p_idx) != -1:
                predicted_text += char_list[int(p_idx)]

    return predicted_text

# Example usage
if __name__ == "__main__":
    image_path = "2022-04-01_09-03-42_UTC.jpg"
    predicted_text = customocr(image_path)
    print("Predicted Text:", predicted_text)