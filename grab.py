from SimpleCV import Camera, JpegStreamer
import time, webbrowser
# Initialize the camera
cam = Camera()
#create JPEG streamers
js = JpegStreamer(8080)
#cam.getDepth().save(js)
webbrowser.open("http://localhost:8080", 2)

# Loop to continuously get images
while True:
    # Get Image from camera
    img = cam.getImage()
    # Make image black and white
    img = img.binarize()
    # Draw the text "Hello World" on image
    img.drawText("Hello World!")
    # Show the image
    img.save(js)
    #img.show()