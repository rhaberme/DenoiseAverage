# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 15:44:04 2017

@author: Mauro

The idea of the script is to create a small GUI managing the bandpass filter.
Since Tkinter can import only GIF image, an interface creates the images and
saves them in  a buffer folder, that are then read by the GUI class
"""

#==============================================================================
# Define Imports
#==============================================================================

# TkInter
from tkinter import Tk, PhotoImage, Label, Frame, Canvas, Entry, Button

# sys imports
from os import mkdir 
from os.path import join, split, isdir, splitext
from shutil import rmtree

# matlibplot imports
from scipy.misc import imsave

# my imports
from MyImage_class import MyImage, Mask
from ImageFFT_class import ImgFFT


#==============================================================================
# Define Class managing image
#==============================================================================

def get_pathname(path):
        path, nameext = split(path)
        name, ext = splitext(nameext)
        return path, name, ext


class ImagePath:

    def __init__(self, name, image, bufpath):
        self.image = image
        self.name = name
        self.gifname = join(bufpath, self.name) + '.gif'

class ImageManager:
    
    def __init__(self, imagepathname):
        
        path, name, ext = get_pathname(imagepathname)
        self.mainpath = path
        self.name = name
        self.inimg_name = self.name + ext

        # create the directory for the elaboration
        self.bufpath = join(self.mainpath,self.name)
        if not isdir(self.bufpath):
            mkdir(self.bufpath)

        # open the source image
        self.inimage = ImagePath(self.name, MyImage(), self.bufpath)
        self.inimage.image.read_from_file(imagepathname)
        self.inimage.image.convert2grayscale()
        
        # resize the image and save it in gif format
        self.savegif(self.inimage, (500, 500))
        
        # declare the fourier transform
        self.ftimage = 0
        
        # TODO        
        # findppeak on the better cc
        # represent it with the tkinter canvas
        
    def calculate_bandpass(self, inradius, insmooth, outradius, outsmooth):
        ''' This method calculates the filter and saves the corresponding images
        the power spectrum (self.psimage) and the result of the filter
        (self.iftimage) in the temp folder
        '''
        
        #transfrom the image
        self.ftimage = ImgFFT(self.inimage.image)
        self.ftimage.ft()

        
        # create bandpass mask
        mask = Mask(self.inimage.image.data.shape)
        mask.bandpass(inradius, insmooth, outradius, outsmooth)
        self.ftimage.apply_mask(mask)

        # represent the masked ps
        self.ftimage.power_spectrum()
        self.psimage = ImagePath(self.name + "_ps", self.ftimage.ps, self.bufpath)
        self.savegif(self.psimage, (500, 500))        

        # calculate inverse transform
        self.ftimage.ift()
        self.iftimage = ImagePath(self.name + "ift", self.ftimage.imgifft, self.bufpath)
        self.savegif(self.iftimage, (500, 500))

    def savegif(self,imagepath, size):
        ''' Given a class imagepath and the size of the images, saves into the
        temp folder the associated image
        '''
        
        # calculate ft for resizing
        imft = ImgFFT(imagepath.image.data)
        imft.ft()
        im = imft.resize_image(size[0], size[1])
        
        # save resized image
        imsave(imagepath.gifname, im.data, format = "gif")
        
    def rm(self):
        rmtree(self.bufpath)
        
        
#==============================================================================
# Define GUI Object
#==============================================================================

class MyWidget(object):
    
    def __init__(self, root, mypathtoimage):
        # initialize the frame and the canvas
        self.frame = Frame(root)
        self.frame.pack()    
        self.canvas = Canvas(self.frame, width=1500, height=500)
        self.canvas.grid(row = 0, column = 0)
        
        self.frame.image = {"inimage" : 0, "fft" : 0, "ift" : 0}
        self.canvasposition = {"inimage" : 0, "fft" : 500, "ift" : 1000}
        
        # initializate the helper class
        self.helper = ImageManager(mypathtoimage)
        
        # show the first image
        self.show_image(self.helper.inimage, "inimage")
        
        # create entries for bandpass
        Label(self.frame, text = "band pass values").grid(row = 1, column = 0)
        
        # create a new frame that contains 4 labels 4 entries
        entryframe = Frame(self.frame)
        entryframe.grid(row = 2) 
        
        # define the entry names
        myvariablesnames = ["inradius", "insmooth", "outradius", "outsmooth"]
        std_values = [str(e) for e in [5, 2, 100, 10]] # default bp values
        
        self.entries = {}
        for i, element in enumerate(myvariablesnames):
            Label(entryframe,text = element).grid(column = i * 2, row = 0)
            self.entries[element] = Entry(entryframe)
            self.entries[element].insert(0,  std_values[i])
            self.entries[element].grid(column = i * 2 + 1, row = 0)
        
        # define a button calculate
        
        b = Button(entryframe, text = "Calculate", command = self.calculate)
        b.grid(row = 0, column = 10)
        
        # - todo -
        # load button
        # save image button
        # save single or all images
        # single or united
        # save bp button
        
    
    def calculate(self):
        # get the bandpass valeus
        inradius = self.entries["inradius"].get()
        insmooth = self.entries["insmooth"].get()
        outradius = self.entries["outradius"].get()
        outsmooth = self.entries["outsmooth"].get()

        
        self.helper.calculate_bandpass(int(inradius), int(insmooth), int(outradius), int(outsmooth))
        
        self.show_image(self.helper.psimage, "fft")
        
        self.show_image(self.helper.iftimage, "ift")

    def show_image(self, image, name):
        inimage = PhotoImage(file = image.gifname)
        self.frame.image[name] = inimage
        self.canvas.create_image(self.canvasposition[name],0 , image = inimage, anchor = "nw")

    
#==============================================================================
# Test environment     
#==============================================================================

if __name__ == "__main__":
    
    piccorrpath = "C:/Users/Mauro/Desktop/Vita Online/Programming/Picture cross corr/"
    
    img_path = "C:/Users/Mauro/Desktop/Vita Online/Programming/Picture cross corr/silentcam/dataset24/avg/correlation_images/corr_1497777846958.png"
    img_path = "C:/Users/Mauro/Desktop/Vita Online/Programming/Picture cross corr/Lenna.png"
    img_path = "C:/Users/Mauro/Desktop/Vita Online/Programming/Picture cross corr/silentcam/dataset24/avg/processed_images/proc_1497777845048.png"
    
    img_path = join(piccorrpath, "silentcam/dataset24/avg/results/avg.png")

    # initializate Tk root
    root = Tk()    
    m = MyWidget(root, img_path)
    
    # start the loop
    root.mainloop()
    
    # clean up    
    m.helper.rm()