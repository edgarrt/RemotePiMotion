import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from datetime import datetime
from collections import deque
import imutils

#imoort statements for Email
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

# initialize the camera and grabs a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (400, 304)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(400, 304))

# allow the camera to warmup
time.sleep(0.5)

motion = False
motionDetected = 1 #first frame is always counted

#creates background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2(20,30,False)

#initializes email
fromaddr = "remotepimotion@gmail.com"
toaddr = "edgartrujillo18@gmail.com"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Motion Detected"


# capture frames from the camera
for fram in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image
        # and occupied/unoccupied text

        frame = fram.array
#       image = frame.copy()

        fgmask = fgbg.apply(frame)

        (_,cnts, _) = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

        motion = False

        # loop over the contours
        for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < 2000:
                        motion = False
                        continue

                motion = True

                # compute the bounding box for the contour, draw it on the frame
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                centerX = x + (w/2)
                centerY = y + (h/2)
                center = (centerX , centerY)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
                if motion is True and motionDetected > 0:

                      time = str(datetime.now())

                      cv2.putText(frame, time, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (255, 255, 255), 1)

                      cv2.imwrite("/home/pi/motion" + str(motionDetected) + ".jpg", frame)

                      print"motion detected"

                      body = "Motion detected at " +  time

                      msg.attach(MIMEText(body, 'plain'))

                      file = "motion" + str(motionDetected) + ".jpg"
                      print file
                      filename = "/home/pi/motion" + str(motionDetected) + ".jpg"
                      print filename
                      attachment = open(filename, "rb")

                      part = MIMEBase('application' , 'octet-stream' )
                      part.set_payload((attachment).read())
                      encoders.encode_base64(part)
                      part.add_header('Content-disposition' , "attachment; filename= $

                      msg.attach(part)
                      
                      server = smtplib.SMTP('smtp.gmail.com', 587)
                      server.starttls()
                      server.login(fromaddr, "Raspberry2016")
                      text = msg.as_string()
                      server.sendmail(fromaddr , toaddr, text)


                      motionDetected = motionDetected + 1

# show the frame

        cv2.imshow("Frame", frame)
        cv2.imshow("mask", fgmask)
        cv2.imshow("liveFeed", image)
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                  break

camera.release()
cv2.destroyAllWindows()
server.quit()






