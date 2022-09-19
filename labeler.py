import json
import pdb
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os, os.path
from PIL import Image, ImageTk
from collections import OrderedDict

# Press the green button in the gutter to run the script.
class Labeler(tk.Tk):

    def loadImages(self, *args):
        path = self.dir.get()
        self.valid_imagetypes = [".jpg", ".gif", ".png"]

        for f in os.listdir(path):
            ext = os.path.splitext(f)[1]
            if ext.lower() in self.valid_imagetypes:
                self.imageDict[os.path.splitext(f)[0]] = {}
                self.imagePilList.append(Image.open(os.path.join(path, f)))
            elif f == self.username.get() + ".json":
                # load existing labels
                with open(self.dir.get() + "/" + self.username.get() + ".json", 'r') as labels:
                    existingDict = json.load(labels)
                    for key in existingDict:
                        self.imageDict[key] = existingDict[key]

        self.infoString1, self.infoString2 = self.updateInfoString()
        self.dirinfo1.configure(text=self.infoString1)
        self.dirinfo2.configure(text=self.infoString2)
        self.showNextImage()

    def selectDir(self):
        filepath = filedialog.askdirectory()
        self.dir.set(filepath)

    def sortDict(self):
        tuples = [(key, self.imageDict[key]) for key in self.imageDict]
        self.imageDict = OrderedDict(sorted(tuples, key=lambda x: (len(x[1]), int(''.join(filter(str.isdigit, x[0])))), reverse=False))
        self.iterator = iter(self.imageDict)
        self.hasChanged.set(False)

    def showNextImage(self):
        #reorder dict by amount of labels to show unfinished images first, but only if user has changed something to prevent alternating
        if self.hasChanged.get():
            self.sortDict()

        if self.gotoprevious:
            self.currentkey = self.old_currentkey
            self.gotoprevious = False
        else:
            #Handle StopIteration Exception when the iterator gets to the end, this currently take two clicks on "next" to show the first image again (but who cares)
            try:
                self.old_currentkey = self.currentkey
                self.currentkey = next(self.iterator)
                if self.old_currentkey == self.currentkey:
                    self.currentkey = next(self.iterator)
            except StopIteration as stop:
                self.sortDict()

        for type in self.valid_imagetypes:

            if os.path.exists(os.path.join(self.dir.get(), self.currentkey + type)):
                #load images
                self.currentImage = Image.open(os.path.join(self.dir.get(), self.currentkey + type))

                #resize
                ratio = min(self.grid_bbox(0,0)[2]/self.currentImage.size[0], self.grid_bbox(0,0)[3]/self.currentImage.size[1])
                self.currentImage = self.currentImage.resize((int(self.currentImage.size[0]*ratio), int(self.currentImage.size[1]*ratio)))
                self.currentImage = ImageTk.PhotoImage(self.currentImage)

                self.imageLabel.configure(image=self.currentImage)
                self.imageLabel.image = self.currentImage

                #reset label values to "uncheck"
                self.signalnoise.set(-1)
                self.noisetype.set("")
                #load label values if applicable
                if "signal" in self.imageDict[self.currentkey]:
                    self.signalnoise.set(self.imageDict[self.currentkey]["signal"])
                if "noisetype" in self.imageDict[self.currentkey]:
                    self.noisetype.set(self.imageDict[self.currentkey]["noisetype"])
                if "faulty" in self.imageDict[self.currentkey]:
                    self.faulty.set(self.imageDict[self.currentkey]["faulty"])

                #disable noistype buttons if no noise is preloaded
                if self.signalnoise.get() != 0:
                    for noisetype in self.noisetypebuttons:
                        noisetype["state"] = "disable"
                break

    def save(self):
        if self.signalnoise.get() != -1:
            self.imageDict[self.currentkey]["signal"] = self.signalnoise.get()
        self.imageDict[self.currentkey]["noisetype"] = self.noisetype.get()
        self.imageDict[self.currentkey]["faulty"] = self.faulty.get()
        out_file = open(self.dir.get() + "/" + self.username.get() + ".json", 'w')
        json.dump(self.imageDict, out_file)
        out_file.close()
        self.showNextImage()

    def previous(self):
        self.gotoprevious = True
        self.save()


    def saveexit(self):
        if self.currentkey != "":
            self.imageDict[self.currentkey]["signal"] = self.signalnoise.get()
            self.imageDict[self.currentkey]["noisetype"] = self.noisetype.get()
            self.imageDict[self.currentkey]["faulty"] = self.faulty.get()
            out_file = open(self.dir.get() + "/" + self.username.get() + ".json", 'w')
            json.dump(self.imageDict, out_file)
            out_file.close()
        self.destroy()

    def change(self):
        self.hasChanged.set(True)
        if self.signalnoise.get() == 0:
            for noisetype in self.noisetypebuttons:
                noisetype["state"] = "normal"
        if self.signalnoise.get() == 1:
            self.noisetype.set("")
            for noisetype in self.noisetypebuttons:
                noisetype["state"] = "disable"




    def updateInfoString(self):
        #default for when no dir has been selected
        if self.dir.get() == "":
            infoString1 = "No Directory Selected"
            infoString2 = "Images: -"

        #
        else:
            imagecount = len([f for f in os.listdir(self.dir.get()) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.gif')])
            infoString1 = "Directory: " + self.dir.get()
            infoString2 = "Images: " + str(imagecount)
        return infoString1, infoString2

    def __init__(self):
        super().__init__()
        self.title("Labeler")
        self.geometry("1536x864")
        self.configure(background="white")
        style = ttk.Style(self)
        self.tk.call('source', 'azure.tcl')
        style.theme_use('azure')

        self.username = tk.StringVar()
        self.username.set("labels")
        self.dir = tk.StringVar()
        self.dir.set("")
        self.dir.trace('w', self.loadImages)
        self.signalnoise = tk.IntVar()
        self.signalnoise.set(-1)
        self.faulty = tk.IntVar()
        self.faulty.set(0)
        self.imageDict = {}
        self.imagePilList = []
        self.currentkey = ""
        self.old_currentkey = ""
        self.noisetype = tk.StringVar()
        self.hasChanged = tk.BooleanVar()
        self.hasChanged.set(True)
        self.infoString1, self.infoString2 = self.updateInfoString()
        self.gotoprevious = False

        #only boring layouting beyond this point

        self.columnconfigure(0, weight=3, uniform='column')
        self.columnconfigure(1, weight=1, uniform='column')
        self.rowconfigure(0, weight=1, uniform='row')

        self.user_frame = tk.Frame(self)
        self.user_frame.grid(row=0, column=1, sticky="n", pady=20)

        self.label_frame = tk.Frame(self)
        self.label_frame.grid(column=1, row=0)

        self.navbuttonframe = ttk.Frame(self)
        self.navbuttonframe.grid(column=1, row=0, sticky='s', pady=25)

        self.nameentrylabel = ttk.Label(self.user_frame, text="Username:")
        self.nameentry = tk.Entry(self.user_frame, textvariable=self.username)

        self.dirButton = ttk.Button(self.label_frame, text="Select Image Directory", command=self.selectDir)
        self.dirinfo1 = ttk.Label(self.label_frame, text=self.infoString1)
        self.dirinfo2 = ttk.Label(self.label_frame, text=self.infoString2)

        self.signalbutton = ttk.Radiobutton(self.label_frame, text="[s] Signal", variable=self.signalnoise, value=1, command=self.change)
        self.noisebutton = ttk.Radiobutton(self.label_frame, text="[n] Noise", variable=self.signalnoise, value=0, command=self.change)
        self.faultybutton = ttk.Checkbutton(self.label_frame, text="[f] Faulty", variable=self.faulty, onvalue=1, offvalue=0)

        self.noisetypelabel = ttk.Label(self.label_frame, text="Noise Type:")
        self.noisetypebutton1 = ttk.Radiobutton(self.label_frame, text="[1] Unknown", variable=self.noisetype, value="unknown")
        self.noisetypebutton2 = ttk.Radiobutton(self.label_frame, text="[2] Movement", variable=self.noisetype, value="movement")
        self.noisetypebutton3 = ttk.Radiobutton(self.label_frame, text="[3] Susceptibility Motion", variable=self.noisetype, value="susceptibility_motion")
        self.noisetypebutton4 = ttk.Radiobutton(self.label_frame, text="[4] Cardiac", variable=self.noisetype, value="cardiac")
        self.noisetypebutton5 = ttk.Radiobutton(self.label_frame, text="[5] Sagittal Sinus", variable=self.noisetype, value="sagittal_sinus")
        self.noisetypebutton6 = ttk.Radiobutton(self.label_frame, text="[6] White Matter", variable=self.noisetype, value="white_matter")
        self.noisetypebutton7 = ttk.Radiobutton(self.label_frame, text="[7] MRI", variable=self.noisetype, value="mri")
        self.noisetypebutton8 = ttk.Radiobutton(self.label_frame, text="[8] Non-Brain", variable=self.noisetype, value="non_brain")
        self.noisetypebutton9 = ttk.Radiobutton(self.label_frame, text="[9] Unclassified", variable=self.noisetype, value="unclassified")

        #for iteration
        self.noisetypebuttons = [self.noisetypebutton1, self.noisetypebutton2, self.noisetypebutton3, self.noisetypebutton4,
                              self.noisetypebutton5, self.noisetypebutton6, self.noisetypebutton7, self.noisetypebutton8,
                              self.noisetypebutton9]


        self.nextbutton = ttk.Button(self.navbuttonframe, text="Next", command=self.save)
        self.previousbutton = ttk.Button(self.navbuttonframe, text="Previous", command=self.previous)
        self.exitbutton = ttk.Button(self.navbuttonframe, text="Save & Exit", command=self.saveexit)



        self.spacinglabel1 = ttk.Label(self.label_frame)
        self.spacinglabel2 = ttk.Label(self.label_frame)
        self.spacinglabel3 = ttk.Label(self.label_frame)

        self.nameentrylabel.pack(side="left", pady=5)
        self.nameentry.pack(side="left", pady=5, padx = 20)
        self.dirButton.pack(side='top', anchor='w', pady=10)
        self.dirinfo1.pack(side='top', anchor='w', pady = 0)
        self.dirinfo2.pack(side='top', anchor='w', pady = 1)
        #self.imageinfo.pack(side='top', anchor='w', pady = 1)
        self.spacinglabel1.pack(side='top', anchor='w', pady=10)
        self.signalbutton.pack(side='top', anchor='w', pady=0)
        self.noisebutton.pack(side='top', anchor='w', pady=3)
        self.faultybutton.pack(side='top', anchor='w', pady=0)
        self.noisetypelabel.pack(side='top', anchor='w', pady=2, padx=5)
        self.noisetypebutton1.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton2.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton3.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton4.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton5.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton6.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton7.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton8.pack(side='top', anchor='w', pady=2, padx=35)
        self.noisetypebutton9.pack(side='top', anchor='w', pady=2, padx=35)
        self.spacinglabel2.pack(side='top', anchor='w', pady=5)

        self.spacinglabel3.pack(side='top', anchor='w', pady=5)
        self.nextbutton.pack(side='left', anchor='w', padx=2)
        self.previousbutton.pack(side='left', anchor='w', padx=2)
        self.exitbutton.pack(side='left', anchor='w', padx=2)

        #load the "please select directory" image
        self.defaultImage = Image.open("defaultImage.png")
        self.defaultImage = ImageTk.PhotoImage(self.defaultImage.resize((800, 500)))
        self.imageLabel = tk.Label(self, image=self.defaultImage)
        self.imageLabel.image = self.defaultImage
        self.imageLabel.grid(column=0, row=0)

        #keyboard shortcuts
        self.bind("<Return>", lambda event: self.nextbutton.invoke())
        self.bind("s", lambda event: self.signalbutton.invoke())
        self.bind("n", lambda event: self.noisebutton.invoke())
        self.bind("1", lambda event: self.noisetypebutton1.invoke())
        self.bind("2", lambda event: self.noisetypebutton2.invoke())
        self.bind("3", lambda event: self.noisetypebutton3.invoke())
        self.bind("4", lambda event: self.noisetypebutton4.invoke())
        self.bind("5", lambda event: self.noisetypebutton5.invoke())
        self.bind("6", lambda event: self.noisetypebutton6.invoke())
        self.bind("7", lambda event: self.noisetypebutton7.invoke())
        self.bind("8", lambda event: self.noisetypebutton8.invoke())
        self.bind("9", lambda event: self.noisetypebutton9.invoke())



if __name__ == '__main__':
    self = Labeler()
    self.mainloop()


#TODO Missing functionality:

#broke images button (faulty)
#image reihenfolge

#cant read I button basic no such elemt in array