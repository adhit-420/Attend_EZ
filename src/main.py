"""
This is the python script that will do all tehe facial recognition. 
"""

import cv2
import matplotlib.pyplot as plt
import cvlib as cv
import numpy as np
import urllib.request
import face_recognition
import numpy as npopencv
from cvlib.object_detection import draw_bbox
import concurrent.futures
import csv
from datetime import datetime

url #Provide web server link here
im=None

image_path1 #Provide paths
image_path2 

image1 = face_recognition.load_image_file(image_path1)
image1_encoding = face_recognition.face_encodings(image1)[0]  # Assuming there's only one face in the image

image2 = face_recognition.load_image_file(image_path2)
image2_encoding = face_recognition.face_encodings(image2)[0]  # Assuming there's only one face in the image

known_face_encodings = [image1_encoding, image2_encoding]
known_faces_names = ["Rishi","sai teja"]

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
current_time = now.time()

attendance_file = f'{current_date}_face_attendance.csv'
phone_file = f'{current_date}_cheating.csv'


def detect_person():
    # cv2.namedWindow("Face Detection", cv2.WINDOW_AUTOSIZE)
    with open(attendance_file, 'w+') as csvfile:
        lnwriter1 = csv.writer(csvfile)
        while True:
            img_resp=urllib.request.urlopen(url)
            imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
            im = cv2.imdecode(imgnp,-1)

            rgb_im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_im)
            face_encodings = face_recognition.face_encodings(rgb_im, face_locations)

            for face_encoding in face_encodings:
                # Compare the current face encoding with known face encodings
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "No face detected!!!"  # Default name if no match found

                # If a match is found, use the name associated with that face encoding
                if True in matches:
                    match_index = matches.index(True)
                    name = known_faces_names[match_index]
                    # print(f"Found Face {name}")
                    lnwriter1.writerow([name, current_time])

                # Draw a rectangle and label for the face
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(im, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(im, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


            cv2.imshow('face detection',im)
            
            if cv2.waitKey(1)==ord('q'):
                break
                
        cv2.destroyAllWindows()
            
def detect_object():
    # cv2.namedWindow("Object Detection", cv2.WINDOW_AUTOSIZE)
    with open(phone_file,'w+') as csvfile2:
        lnwriter2 = csv.writer(csvfile2)
        while True:
            img_resp=urllib.request.urlopen(url)
            imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
            im = cv2.imdecode(imgnp,-1)
    
            bbox, label, conf = cv.detect_common_objects(im)
            im = draw_bbox(im, bbox, label, conf)

            if "cell phone" in label:
                current_time = now.time()
                print(f"Cell phone found at !!pls check. Time: {current_time}")
                lnwriter2.writerow(['Phone detected', current_time])

            cv2.imshow('Object Detection',im)
            if cv2.waitKey(1)==ord('q'):
                break
                
        cv2.destroyAllWindows()
    
 
if __name__ == '__main__':
    print("started")
    print(current_date)
    with concurrent.futures.ProcessPoolExecutor() as executer:
            f1= executer.submit(detect_person)
            f2= executer.submit(detect_object)
