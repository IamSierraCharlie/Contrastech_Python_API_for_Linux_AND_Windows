# Contrastech_Python_API_for_Linux
### What this is
A very (very) basic working version of a python API for Contrastech MARS model USB 3.0 cameras.
I own a couple of Contrastech MARS cameras http://www.contrastech.com/content/?875.html
and have had to use 3rd party API's to get Windows functionality for these cameras in Python. 
Let me be the first to say that the one I have used has been very good for what I need, but other than Aravis, I have 
not been able to find anything that works for Linux for Python that allows grabbing of images in an numpy nd.array style image grab.
Contrastech was good enough to provide an example of some code that grabbed images and saved them as a BMP.  This code I have written is
very basic, but allows grabbing of an numpy nd.array style image.
It should be noted that I have fumbled my way to this point to get some working code - I do not profess to be an expert.  My reason for
adding this repo is in the hope that some that others may be able to benefit from it as well as contribute to a better version of the
code.  This API uses c_types to interface with the dll which is provided by Contrastech.  I have very limited experience with c_types in Python 

### Known working cameras - tested and confirmed
- Mars1300-210uc
Other Mars cameras from Contrastech should work also.

If you own one of these cameras and work in Linux and can use this code, then please do so.  Also, please contribute anything you feel to be of benefit.
### Example use
The script 'image_grab_demo.py' is provided as an example to show the code working - again, very basic.
Essentially, I have historically created an instance of the camera, activated the camera, grabbed an image and then deactivated it
Contrastech provided a very basic demo and I have only used that demo to make what is provided. 

### Prerequisites
- An install of Python on a Linux Operating System (I used Anaconda with Python 3.6 on Ubuntu 16.04  )
- Python Modules -> c_types, opencv2, numpy
- The Contrastech Software Development Kit for Linux (x86) (aka iCentral) - this includes the driver required to run the camera in Linux and can be found at http://contrastech.com/content/?906.html

### Getting this SDK to work
Review and/or run ImageGrabDemo.py with a Contrastech USB3 Camera such as the Mars 1300-201uc and it should work.  There
are examples on how to send commands to the camera.  It is recommended you review the Contrastech SDK for commands that 
work.  Another useful place is the XML file stored on the camera (every camera keeps a file on it that provides its 
functionality)

### Known Issues
- the version of opencv to install should be from the menpo channel - install with 'conda install -c menpo opencv3'
- the software and driver from ContrasTech is only known to work up to Ubuntu 16.04.  I have checked with the support 
team (October 2020) and they confirm this.  The main issue is that the driver won't build on kernel versions beyond 
what is offered in newer versions of Ubuntu.
- Program is likely to stop working when the Kernel is updated.  You need to reinstall the driver to the current kernel 
for it to work properly.  A giveaway for this issue is that the program complains that it is unable to load the driver.  
The fix is to reinstall iCentral which will compile the module and install again. 
- my code writing is crap - yes I know.  I cannot commit the time I want to for these things, but I'm working on it.  
Constructive criticisms is always appreciated...

### Feedback
If you own this camera or use this API, please provide feedback.  If you want to collaborate on this or your own work, 
I'm happy to offer a hand.  I admit I am no expert, but am always keen on seeing the development of an SDK for this 
camera as there is not a huge amount of info out there for this.

### Future plans
- my reason for this code was that I took high speed images on a production line for quality checks using Tensorflow.  I
ran this in Windows for the most part due to this driver issue.  I did have success in getting my program to 
work in Linux although I never put it into production.  I plan to make some changes to this code so that the camera will 
accept a signal from an external sensor to time the image grabs as opposed to just grabbing an image every
N seconds.  Timing is everything ona production line!  If you are doing something similar, I'd be keen to hear about it!

- Other cool things - if you could get it to work on a Raspberry Pi, you could use Tensorflow to read speed signs or stop signs...
- I have a Daheng Mercury camera also.  I have done some testing on it and some of it works.  You can grab camera details,
but not much else. It leads me to believe that I am not far from building something that might work for multiple cameras.  
I guess every camera manufacturer has a subtle way of doing the same thing a little differently.  Perhaps there is an 
opportunity to get functionality on other cameras? 
- My focus is on a production line though...

### Working Example
Here is my dog Pip
![working_example](https://user-images.githubusercontent.com/10386637/43674828-ce240cb2-981c-11e8-9265-56a9268cf157.png)


