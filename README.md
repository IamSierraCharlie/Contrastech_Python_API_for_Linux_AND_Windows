# ContrasTech_Python_API_for_Linux_And_Windows
### What this is
A working version of a python API for ContrasTech MARS model USB3 Industrial cameras.  This camera doesn't use the standard openCV method of grabbing an image.  It conforms to the 
GeniCam standard (See https://www.emva.org/standards-technology/genicam/genicam-downloads/) I own a couple of ContrasTech 
MARS cameras http://www.ContrasTech.com/content/?875.html and have had to use 3rd party APIs to get Windows functionality 
for these cameras in Python.  Let me be the first to say that the one I have used has been very good for what I need, but 
other than Aravis, I have not been able to find anything that works for Linux for Python that allows grabbing of images 
in a numpy nd.array style image grab; at least not for this camera under Linux.  ContrasTech was good enough to 
provide an example of some code that grabbed images and saved them as a BMP and I have gone from there to produce this
code.  This code I have written is pretty basic, but allows grabbing of a numpy nd.array style image.  It should be 
noted that I have fumbled my way to this point to get some working code - I do not profess to be an expert.  My reason 
for adding this repo is in the hope that some that others may be able to benefit from it as well as contribute to a better 
version of the code.  This API uses c_types to interface with the dll which is provided by ContrasTech.  I have very 
limited experience with c_types in Python, but this seems to work just fine - NOW IN BOTH WINDOWS AND LINUX!!!

### Why use it??
The main reason is ease of use; if you have little understanding of c_types AND want to use your ContrasTech camera in Linux, then this API makes it easier to set 
up your USB3 Industrial camera.  Getting and setting parameter values is very easy also.  

### Known working cameras 
Tested and confirmed on the following Industrial USB3 Camera
- Mars1300-210uc
Any other Mars USB3 camera from ContrasTech should work also.
With some minor adjustments, you could probably use this for a GIG-E camera also.

If you own one of these cameras and work in Linux and can use this code, then please do so.  Also, please contribute anything you feel to be of benefit.
### Example use
The script 'image_grab_demo.py' is provided as an example to show the code working - again, very basic.
Essentially, I have historically created an instance of the camera, activated the camera, grabbed an image and then deactivated it
ContrasTech provided a very basic demo, and I have only used that demo to make what is provided. 

### Prerequisites
- An installation of Python on a Linux Operating System (I used Anaconda with Python 3.6 on Ubuntu 16.04  ) As of 2022, I am 
using Ubuntu 20.04 and whilst not officially supported by ContrasTech, it works without issue.
- Python Modules -> c_types, opencv2, numpy
- The ContrasTech Software Development Kit for Linux (x86) (aka iCentral) - this includes the driver required to run the 
camera in Linux and can be found at http://www.contrastech.com/upload/down/Mars/Linux/iCentral_Ver2.2.6_Linux_x86_Build20210705.zip

### Getting this API to work
Review and/or run ImageGrabDemo.py with a ContrasTech USB3 Camera such as the Mars 1300-201uc, and it should work.  There
are examples on how to send commands to the camera.  It is recommended you review the ContrasTech SDK for commands that 
work; as well as the iCentral program supplied by ContrasTech.  Another useful place is the XML file stored on the camera (every camera keeps a file on it that provides its 
functionality).  Review the ImageGrabDemo.py file and the XML file in conjunction.  You can set properties or get property 
values by first creating a camera instance and then calling the 'property_getset' command.  Where the second argument 
is populated, the function will attempt to set a value for the property in question.  If you call 'property_getset' without a value, then it will get 
the stored value.  This API DOES work in Windows AND I've tested it; although there are a few little buggy issues that need work.


### Known Issues
- For Linux, the software and driver from ContrasTech is confirmed to work up to Ubuntu 20.04.  On October 2020, I checked with 
ContrasTech support and they only supported up to 16.04, but I currently run on 20.04 (as of Feb 2022) and haven't noticed any issues. 
- Works in Windows although I've found on occasion that the API fails to get the software trigger to go.  As a result, 
image grab fails.  The workaround seems to be to close your IDE and try again or restart.  I will provide a fix when I confirm
the issue and have some more time.
- Linux - Program may stop working when the Kernel is updated.  You need to reinstall the driver to the current kernel 
for it to work properly.  A giveaway for this issue is that the program may complain that it is unable to load the driver.  
The fix is to reinstall iCentral which will compile the module and install again. 
- my code writing is crap - yes I know.  I cannot commit the time I want to for these things, but I'm working on it.  
Constructive criticisms is always appreciated...

### Feedback
If you own this camera or use this API, please provide feedback.  If you want to collaborate on this or your own work, 
I'm happy to offer a hand.  I admit I am no expert, but am always keen on seeing the development of an API for this 
camera as there is not a huge amount of info out there for this.

### Future plans
- my reason for this code was that I took high speed images on a production line for quality checks using Tensorflow.  I
ran this in Windows for the most part due to this driver issue.  I did have success in getting my program to 
work in Linux, although I never put it into production.  I plan to make some changes to this code so that the camera will 
accept a signal from an external sensor to time the image grabs as opposed to just grabbing an image every
N seconds.  Timing is everything on a production line!  If you are doing something similar, I'd be keen to hear about it!

- Other cool things - if you could get it to work on a Raspberry Pi, you could use Tensorflow to read speed signs or stop signs...
- I have a Daheng Mercury camera also.  I have done some testing on it and some of it works.  You can grab camera details,
but not much else. It leads me to believe that I am not far from building something that might work for multiple cameras.  
I guess every camera manufacturer has a subtle way of doing the same thing a little differently.  Perhaps there is an 
opportunity to get functionality on other cameras? 
- My focus is on a production line though...

### Working Example
Here is my dog Pip
![working_example](https://user-images.githubusercontent.com/10386637/43674828-ce240cb2-981c-11e8-9265-56a9268cf157.png)


