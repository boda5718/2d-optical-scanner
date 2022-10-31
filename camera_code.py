#===========================================================================#
# Developer Note: I tried to let it as simple as possible.
# Therefore there are no functions asking for the newest driver software or freeing memory beforehand, etc.
#---------------------------------------------------------------------------------------------------------------------------------------

#Libraries
from pyueye import ueye
import numpy as np
import cv2
import serial
import time
from time import sleep
import sys
from PIL import Image


#---------------------------------------------------------------------------------------------------------------------------------------

#Variables
hCam = ueye.HIDS(0)             #0: first available camera;  1-254: The camera with the specified camera ID
sInfo = ueye.SENSORINFO()
cInfo = ueye.CAMINFO()
pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()
rectAOI = ueye.IS_RECT()
pitch = ueye.INT()
nBitsPerPixel = ueye.INT(8)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
channels = 1                    #3: channels for color mode(RGB); take 1 channel for monochrome
m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
bytes_per_pixel = int(nBitsPerPixel / 8)
#---------------------------------------------------------------------------------------------------------------------------------------
print("START")
print()


# Starts the driver, serial communication with arduino, and establishes the connection to the camera
arduino = serial.Serial('COM6', 9600)
time.sleep(2)

nRet = ueye.is_InitCamera(hCam, None)
if nRet != ueye.IS_SUCCESS:
    print("is_InitCamera ERROR")

# Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
nRet = ueye.is_GetCameraInfo(hCam, cInfo)
if nRet != ueye.IS_SUCCESS:
    print("is_GetCameraInfo ERROR")

# You can query additional information about the sensor type used in the camera
nRet = ueye.is_GetSensorInfo(hCam, sInfo)
if nRet != ueye.IS_SUCCESS:
    print("is_GetSensorInfo ERROR")

nRet = ueye.is_ResetToDefault( hCam)
if nRet != ueye.IS_SUCCESS:
    print("is_ResetToDefault ERROR")

# Set display mode to DIB
nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)

# Set the right color mode

# for monochrome camera models use Y8 mode
m_nColorMode = ueye.IS_CM_MONO8
nBitsPerPixel = ueye.INT(8)
bytes_per_pixel = int(nBitsPerPixel / 8)
print("else")

# Can be used to set the size and position of an "area of interest"(AOI) within an image
nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
if nRet != ueye.IS_SUCCESS:
    print("is_AOI ERROR")

width = rectAOI.s32Width
height = rectAOI.s32Height

# Prints out some information about the camera and the sensor
print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
print("Maximum image width:\t", width)
print("Maximum image height:\t", height)
print()

#---------------------------------------------------------------------------------------------------------------------------------------

# Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
if nRet != ueye.IS_SUCCESS:
    print("is_AllocImageMem ERROR")
else:
    # Makes the specified image memory the active memory
    nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetImageMem ERROR")
    else:
        # Set the desired color mode
        nRet = ueye.is_SetColorMode(hCam, m_nColorMode)



## Activates the camera's live video mode (free run mode)
#nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)
#if nRet != ueye.IS_SUCCESS:
    #print("is_CaptureVideo ERROR")
nRet = ueye.is_SetExternalTrigger(hCam, ueye.IS_SET_TRIGGER_SOFTWARE)
if nRet != ueye.IS_SUCCESS:
    print("is_SetExternalTrigger ERROR")



# Enables the queue mode for existing image memory sequences
nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
if nRet != ueye.IS_SUCCESS:
    print("is_InquireImageMem ERROR")


#---------------------------------------------------------------------------------------------------------------------------------------

# Continuous image display (25 snapshots covers 25*6.1mm=15.25cm)
count = 0
while( count<25 ):

    nRet = ueye.is_FreezeVideo(hCam, ueye.IS_WAIT)
    if nRet != ueye.IS_SUCCESS:
        print("is_FreezeVideo ERROR")
    arduino.write(b'1')
    # In order to display the image in an OpenCV window we need to...
    # ...extract the data of our image memory
    array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)

    # bytes_per_pixel = int(nBitsPerPixel / 8)

    # ...reshape it in an numpy array...
    frame = np.reshape(array, (height.value, width.value, bytes_per_pixel))

    # ...resize the image to decrease the pixels
    frame = cv2.resize(frame, (0, 0), fx=0.015, fy=0.015)


    # ...save the scanned image...
    # ...any file destination in the code must be changed according to your device or you will get bunch of errors...
    cv2.imwrite(r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\snapshot%d.jpg' % count, frame)

    #...combine the snapshots horizontaly

    if(count==1):

        images = [Image.open(x) for x in [r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\snapshot0.jpg' ,
                                          r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\snapshot%d.jpg' % count]]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        new_im.save(r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\new_combined_snapshots.jpg')

    #####################################################################################################

    if (count>1):
        images = [Image.open(x) for x in [r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\new_combined_snapshots.jpg',
                                          r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\snapshot%d.jpg' % count ]]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        new_im.save( r'C:\Users\Boda\Desktop\savedImagesOpencv\scan1\new_combined_snapshots.jpg')

    count += 1
    sleep(1)


# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)

# Disables the hCam camera handle and releases the data structures and memory areas taken up by the uEye camera
ueye.is_ExitCamera(hCam)

# Destroys the OpenCv windows
cv2.destroyAllWindows()

print()
print("END")
