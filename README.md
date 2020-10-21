# Contrastech_Python_SDK_for_Linux
### What this is
A very (very) basic working version of a python SDK for Contrastech MARS model USB 3.0 cameras.
I own a couple of Contrastech MARS cameras http://www.contrastech.com/content/?875.html
and have had to use 3rd party SDK's to get Windows functionality for these cameras in Python. 
Let me be the first to say that the one I have used has been very good for what I need, but other than Aravis, I have 
not been able to find anything that works for Linux for Python that allows grabbing of images in an numpy nd.array style image grab.
Contrastech was good enough to provide an example of some code that grabbed images and saved them as a BMP.  This code I have written is
very basic, but allows grabbing of an numpy nd.array style image.
It should be noted that I have fumbled my way to this point to get some working code - I do not profess to be an expert.  My reason for
adding this repo is in the hope that some that others may be able to benefit from it as well as contribute to a better version of the
code.  This SDK uses c_types to interface with the dll which is provided by Contrastech.  I have very limited experience with c_types in Python 

### Known working cameras - tested and confirmed
- Mars1300-210uc
Other Mars cameras from Contrastech should work also.

If you own one of these cameras and work in Linux and can use this code, then please do so.  Also, please contribute anything you feel to be of benefit.
### Example use
The script 'image_grab_demo.py' is provided as an example to show the code working - again, very basic.
Essentially, I have historically created an instance of the camera, activated the camera, grabbed an image and then deactivated it
Contrastech provided a very basic demo and I have only used that demo to make what is provided. 

### Prerequisites
- An install of Python on a Linux Operating System ( I used Anaconda with Python 3.6 on Ubuntu 16.04  )
- Python Modules -> c_types, opencv2, numpy

### Working Example

Here is my dog Pip
![working_example](https://user-images.githubusercontent.com/10386637/43674828-ce240cb2-981c-11e8-9265-56a9268cf157.png)
