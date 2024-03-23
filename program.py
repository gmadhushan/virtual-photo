#Import the necessary libraries
import os
import cv2
import random
import numpy as np

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

from tkinter.simpledialog import askstring
from tkinter import *
from PIL import Image

#User defined function to sendmail
def sendMail(to, subject, text, files=[]):
    assert type(to)==list
    assert type(files)==list
    
    USERNAME = " "      #Type the google mail id from which the mail is to be sent
    PASSWORD = " "      #Create an app password for the google account in account settings>>security and paste it here
         
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, to, msg.as_string())
    server.quit()
    
#User defined function to remove green background
def remove_green_screen(image,background_image):
    # Input arguments are image taken from camera and background image to insert
  
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define range of green color in HSV
    lower_green = np.array([80, 85, 70])
    upper_green = np.array([100, 255, 255])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    masked_background = cv2.bitwise_and(background_image, background_image, mask=mask)

    # Invert the mask
    mask = cv2.bitwise_not(mask)

    # Bitwise-AND mask and original image
    result = cv2.bitwise_and(image, image, mask=mask)
    result_image = cv2.add(result, masked_background)

    return result_image

def click_photo(email):
    
    thank_msg = " "
    email_id = [email]

    os.chdir("/home/Desktop/virtual_photo") #Path of background image and template image folders
    dest_folder = "merged_photos"           #Path of a destination folder to save final output images
    
    bg_choices = os.listdir("bg_choices")    #Path of background image folder
    bg = random.choice(bg_choices)
    bg_img = cv2.imread(os.path.join("bg_choices",bg))
    
    cam = cv2.VideoCapture(0)
    result, image = cam.read()
    cam.release()
    
    #image = cv2.imread("/home/Desktop/virtual_photo/Bgtest.jpg")    #To test on an already captured image
    bg_image = cv2.resize(bg_img,(image.shape[1], image.shape[0]))
    in_image = remove_green_screen(image, bg_image)
    temp_img = cv2.resize(in_image, (400,400))
    to_paste_img = Image.fromarray(cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB))
    
    card_choices = os.listdir("card_choices")       #Path of card template image folder
    card = random.choice(card_choices)
    card_img = Image.open(os.path.join("card_choices",card))
    
    card_img.paste(to_paste_img,(600,600))
    #bg_img.show()
    merged_photo = email_id[0] + '.jpg'     #Name the final output image as email_id.jpg
    card_img.save(os.path.join(dest_folder, merged_photo))  #Save the final output image in the destination folder
    img_to_send = os.path.join(dest_folder, merged_photo)   #Path of the saved final output image    
    
    sendMail(email_id, "Type the subject of the email", thank_msg, [img_to_send])  

top = Tk()
top.title("Photo Point")    #Title of the tkinter GUI
canvas= Canvas(top, width= 1500, height= 1500, bg="gold")   #create a canvas
msg1 = "WELCOME"
msg2 = "HAVE A GOOD DAY"
msg3 = "This is a program to take photo and merge with a virtual background"
msg4 = "PHOTO POINT"
msg5 = "Enter your Email ID:"
canvas.create_text(750, 50, text=msg1, fill="black", font=('Helvetica 30 bold'))     # Overlay the custom text on the canvas at a given location
canvas.create_text(750, 90, text=msg2, fill="black", font=('Helvetica 30 bold'))
canvas.create_text(750, 150, text=msg3, fill="black", font=('Helvetica 30 bold'))
canvas.create_text(750, 220, text=msg4, fill="green4", font=('Helvetica 30 bold'))
canvas.create_text(750, 400, text=msg5, fill="red2", font=('Helvetica 30 bold'))

entry = Entry(top) 
canvas.create_window(750, 450, window=entry, height = 30, width = 400)   #create a text entry object on the canvas for email id user input

def get_email():  
    mail_id = entry.get()
    click_photo(mail_id)
    entry.delete(0, END)

button = Button(top, text='Click Photo', width=10, height=2, bd='5', command=get_email) #create a button on the canvas and trigger the functions upon click
button.place(x=870, y=500)
canvas.pack()

top.mainloop()
