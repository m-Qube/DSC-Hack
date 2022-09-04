from email import message
from flask import Blueprint, render_template, request, redirect, session, url_for,Response
import pymongo, bcrypt
#from att import out
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# from PIL import ImageGrab

path = '/home/ayush/Desktop/DSC-Hack/ds01/website/Training_images'
images = []
classNames = []
myList = os.listdir(path)
#print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
#print(classNames)


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()

        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')

encodeListKnown = findEncodings(images)
#print('Encoding Complete')

#cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

def out(cap):
    #while True:
        cv2.waitKey(1)
        success, img = cap.read()
        imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                ret, jpeg = cv2.imencode('.jpg', img)
                return jpeg.tobytes(),[True,name]
                #markAttendance(name)
        
        ret, jpeg = cv2.imencode('.jpg', img)
        #cv2.imshow('Webcam', img)
        
        return jpeg.tobytes(),[False,'n/a']

auth = Blueprint('auth', __name__)

client = pymongo.MongoClient("mongodb+srv://srm:2024@cluster0.ec8b1tz.mongodb.net/test")
db = client.get_database('total_records')
records = db.register

message = ''
@auth.route('/signup/', methods = ['GET', 'POST'])
def sign_up():
    global message
    if "user" in session:
        return redirect(url_for('/dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')

        password = request.form.get('password')
        confirm_pass = request.form.get('confirm_pass')
        #Checking whether email is already registered or not
        email_found = records.find_one({"email":email})
        
        if email_found:
            message = 'This email already exists'
            return redirect(url_for('/login'), message = message )

        if password!=confirm_pass:
            message = 'Passwords should match!'
            return render_template('signup.html',message = message)
        
        else:
            
            #hashing the password and encoding it
            hashed = bcrypt.hashpw(confirm_pass.encode('utf-8'), bcrypt.gensalt())

            #assigning the data in a dictionary in key value pairs
            user_input = {'email': email, 'name': name, 'password': hashed}
            #inserting it in the record collection
            records.insert_one(user_input)
            message = 'successfully sent :)'
    return render_template('signup.html', message = message)


@auth.route('/', methods = ['GET', 'POST'])
def index():
    message = ""
    if 'user' in session:
        print('check123')
        return redirect(url_for('/dashboard'))
    if request.method == 'POST':
        user = request.form.get('email')
        password = request.form.get('password')
        user_found = records.find_one({'email':user})
        if user_found:

            passwordcheck = user_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["emailid"] = user
                message = "Welcome user "
                return redirect('/dashboard')
            else:
                message = "Wrong password"
                return render_template('login.html',message = message)
        else:
            message = 'User not found'
            return render_template('login.html', message = message)
    return render_template('login.html', message = message)

@auth.route('/dashboard/')
def dashboard():
    if 'user' in session:
        user = session['user']
        return render_template('dashboard.html')
    else:
        message = 'Please login into your account!'
        return render_template('dashboard.html') #redirect(url_for('login'))
    #return render_template('dashboard.html', message = message)


@auth.route("/logout/")
def logout():
    if "user" in session:
        session.pop("user", None)
        return redirect('/')
    else:
        return redirect('/')


@auth.route("/cam/")
def cam():
    if "user" in session:
        return render_template('cam.html')
    else:
        return render_template('cam.html')


m= False
@auth.route('/attendance')
def att():
    global m
    print(m)
    return render_template('attendance.html',enable = m)

def gen():
    cap = cv2.VideoCapture(0)
    while True:
        try:
            frame,marked = out(cap)
            if marked:
                print(marked)
        except:
            frame,marked = out(cap)
            print(marked)

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if marked[0]==True:
            global m
            m= marked
            
            
        

@auth.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')