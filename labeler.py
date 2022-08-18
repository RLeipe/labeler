import json
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
            elif f == "labels.json":
                # load existing labels
                with open(self.dir.get() + "/labels.json", 'r') as f:
                    existingDict = json.load(f)
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
        self.imageDict = OrderedDict(sorted(tuples, key=lambda x: len(x[1]), reverse=False))
        self.iterator = iter(self.imageDict)
        self.hasChanged.set(False)

    def showNextImage(self):
        #reorder dict by amount of labels to show unfinished images first, but only if user has changed something to prevent alternating
        if self.hasChanged.get():
            self.sortDict()

        #Handle StopIteration Exception when the iterator gets to the end, this currently take two clicks on "next" to show the first image again (but who cares)
        try:
            old_currentkey = self.currentkey
            self.currentkey = next(self.iterator)
            if old_currentkey == self.currentkey:
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
                self.signalnoise = -1
                self.confidence = -1
                #load label values if applicable
                if "signalnoise" in self.imageDict[self.currentkey]:
                    self.signalnoise.set(int(self.imageDict[self.currentkey]["signal"]))
                if "confidence" in self.imageDict[self.currentkey]:
                    self.confidence.set(self.imageDict[self.currentkey]["confidence"])
                break

    def save(self):
        self.imageDict[self.currentkey]["confidence"] = self.confidence.get()
        self.imageDict[self.currentkey]["signal"] = self.signalnoise.get()
        out_file = open(self.dir.get() + "/labels.json", 'w')
        json.dump(self.imageDict, out_file)
        out_file.close()
        self.showNextImage()

    def saveexit(self):
        if self.currentkey != "":
            self.imageDict[self.currentkey]["confidence"] = self.confidence.get()
            self.imageDict[self.currentkey]["signal"] = bool(self.signalnoise.get())
            out_file = open(self.dir.get() + "/labels.json", 'w')
            json.dump(self.imageDict, out_file)
            out_file.close()
        self.destroy()

    def change(self):
        self.hasChanged.set(True)

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

        self.dir = tk.StringVar()
        self.dir.set("")
        self.dir.trace('w', self.loadImages)
        self.signalnoise = tk.IntVar()
        self.signalnoise.set(2)
        self.confidence = tk.IntVar()
        self.imageDict = {}
        self.imagePilList = []
        self.currentkey = ""
        self.hasChanged = tk.BooleanVar()
        self.hasChanged.set(True)
        self.infoString1, self.infoString2 = self.updateInfoString()

        #only boring layouting beyond this point

        self.columnconfigure(0, weight=3, uniform='column')
        self.columnconfigure(1, weight=1, uniform='column')
        self.rowconfigure(0, weight=1, uniform='row')

        self.label_frame = tk.Frame(self)
        self.label_frame.grid(column=1, row=0)
        self.label_frame.configure(background="white")


        self.dirButton = ttk.Button(self.label_frame, text="Select Image Directory", command=self.selectDir)
        self.dirinfo1 = ttk.Label(self.label_frame, text=self.infoString1)
        self.dirinfo2 = ttk.Label(self.label_frame, text=self.infoString2)

        self.signalbutton = ttk.Radiobutton(self.label_frame, text="Signal", variable=self.signalnoise, value=1, command=self.change)
        self.noisebutton = ttk.Radiobutton(self.label_frame, text="Noise", variable=self.signalnoise, value=0, command=self.change)

        self.conf1 = ttk.Radiobutton(self.label_frame, text="1", variable=self.confidence, value=1, command=self.change)
        self.conf2 = ttk.Radiobutton(self.label_frame, text="2", variable=self.confidence, value=2, command=self.change)
        self.conf3 = ttk.Radiobutton(self.label_frame, text="3", variable=self.confidence, value=3, command=self.change)

        self.savebutton = ttk.Button(self.label_frame, text="Next", command=self.save)
        self.exitbutton = ttk.Button(self.label_frame, text="Save & Exit", command=self.saveexit)

        self.spacinglabel1 = ttk.Label(self.label_frame)
        self.spacinglabel2 = ttk.Label(self.label_frame)
        self.spacinglabel3 = ttk.Label(self.label_frame)
        self.confidenceLabel = ttk.Label(self.label_frame, text="Confidence:")


        self.dirButton.pack(side='top', anchor='w', pady=10)
        self.dirinfo1.pack(side='top', anchor='w', pady = 0)
        self.dirinfo2.pack(side='top', anchor='w', pady = 1)
        self.spacinglabel1.pack(side='top', anchor='w', pady=10)
        self.signalbutton.pack(side='top', anchor='w', pady=0)
        self.noisebutton.pack(side='top', anchor='w', pady=3)
        self.spacinglabel2.pack(side='top', anchor='w', pady=5)
        self.confidenceLabel.pack(side='top', anchor='w', pady=5)
        self.conf1.pack(side='top', anchor='center', pady=1)
        self.conf2.pack(side='top',  anchor='center', pady=1)
        self.conf3.pack(side='top',  anchor='center', pady=1)
        self.spacinglabel3.pack(side='top', anchor='w', pady=5)
        self.savebutton.pack(side='top', anchor='w', pady=15)
        self.exitbutton.pack(side='top', anchor='w', pady=0)

        #load the "please select directory" image
        self.defaultImage = Image.open("defaultImage.png")
        self.defaultImage = ImageTk.PhotoImage(self.defaultImage.resize((800, 500)))
        self.imageLabel = tk.Label(self, image=self.defaultImage, bg="blue4")
        self.imageLabel.image = self.defaultImage
        self.imageLabel.grid(column=0, row=0)








if __name__ == '__main__':
    self = Labeler()
    self.mainloop()


#TODO Missing functionality:

#increase Font Size
#automatically uncheck
#error for unfinished input
#lastimage button
#textfield für direktes ansprechen
#name des raters

#cant read I button basic no such elemt in array