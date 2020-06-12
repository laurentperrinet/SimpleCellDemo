#!/usr/bin/env python

"""

SimpleReceptiveField.py : linking the webcam to a crude-but-adaptive neuron and
let it spike in the loudspeaker.

Laurent Perrinet, 2010. Credits: see https://github.com/laurentperrinet/SimpleCellDemo

this depends on OpenCV + numpy + pil, which intalls fine with HomeBrew: {{{
brew install opencv
}}}

Credits: see pysight.py and EgoViewer.py

$Id: SimpleReceptiveField.py,v 3ff3065a2f2d 2011/04/13 14:46:44 perrinet $

"""
try:
    import pyaudio
    AUDIO = True
except:
    print('Could not import pyaudio, disabling sound')
    AUDIO = False

from numpy import zeros, linspace, hstack, transpose, pi
import numpy as np
from SimpleCV import Camera, Display, Color

import numpy as np
import time
import sys

# TODO : plot histogram and membrane potential
# TODO : remove background of RF

#########################################################
#########################################################
NUM_SAMPLES = 1024
# neural parameters
spike = 255*np.ones(45) # that's a crude spike!
quant = 512
rate = 0.01
adaptive = True
sample = 5
sigma = 8.

#============================================================================
# Set up input
#============================================================================
def do_RF(bb):

    img = cam.getImage().smooth()
    img = img.smooth()#.flipHorizontal()
#     img = img.edges()
    img = img.crop(bb)
    img_np = img.getNumpy().mean(axis=2).T
    img_np += 1e-12
    img_np /= np.sqrt(np.sum(img_np**2))
    return img, img_np


def getBBFromUser(cam, d):
    p1 = None
    p2 = None
    img = cam.getImage()
    while d.isNotDone():
        try:
            img = cam.getImage()
            img.save(d)
            dwn = d.leftButtonDownPosition()
            up = d.leftButtonUpPosition()

            if dwn:
                p1 = dwn
            if up:
                p2 = up
                break

            time.sleep(0.05)
        except KeyboardInterrupt:
            break
    print p1,p2
    if not p1 or not p2:
        return None

    xmax = np.max((p1[0],p2[0]))
    xmin = np.min((p1[0],p2[0]))
    ymax = np.max((p1[1],p2[1]))
    ymin = np.min((p1[1],p2[1]))
    print xmin,ymin,xmax,ymax
    return (xmin,ymin,xmax-xmin,ymax-ymin)
#============================================================================
# Create the model.
#============================================================================
corr = 0
voltage = 0.5
hist = np.ones(quant) / quant

def neuron(im, voltage, hist):
    if voltage > 1.: voltage = 0.
    corr = np.dot(im.ravel(), RF.ravel()) #result[0, 0]
    quantile = int(((corr+1)/2) * quant)-1
    if adaptive:
        cumhist = np.cumsum(hist)
        voltage = cumhist[quantile]
        if voltage > .9:
            if AUDIO: stream.write(spike)
            voltage = 2.

        hist[quantile] += rate
        hist /= np.sum(hist)

    else:
        if corr > .15:
            if AUDIO: stream.write(spike)

    return corr, voltage
#============================================================================
if __name__ == "__main__":

    if AUDIO:
        # open audio stream to the speakers
        p = pyaudio.PyAudio()
        # initialize loudspeaker
        stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True)

    snapshotTime = time.time()
    # check if capture device is OK
    # Initialize the camera
    cam = Camera()
    print 'Camera : ', cam.getProperty("height"), cam.getProperty("width")
    print ' Startup time ', (time.time() - snapshotTime)*1000, ' ms'
    snapshotTime = time.time()

    try:
        img = cam.getImage()
        disp = Display(img.size(), title = "SimpleCellDemo, Draw the RF's bounding box with mouse")
        bb = getBBFromUser(cam, disp)
        disp.quit()
        disp = Display(img.size())
        disp = Display(img.size(), title = "SimpleCellDemo, Press Esc to exit")
        img, RF = do_RF(bb)
        while disp.isNotDone():
            snapshotTime = time.time()
            img, im = do_RF(bb)
            corr, Vm = neuron(im, voltage, hist)
            print corr, Vm
            backshotTime = time.time()
            fps = 1. / (backshotTime - snapshotTime)
            img.drawText("FPS:" + str(fps), 10, 10, fontsize=30, color=Color.GREEN)
            img.show()
        disp.quit()

    finally:
        # Always close the camera stream
        if AUDIO: stream.close()
