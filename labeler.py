import json
import tkinter as tk
from tkinter import filedialog
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

        self.infoString = self.updateInfoString()
        self.dirinfo.configure(text=self.infoString)
        self.showNextImage()

    def selectDir(self):
        filepath = filedialog.askdirectory()
        self.dir.set(filepath)
        # todo: display chosen path somewhere in the frame

    def sortDict(self):
        tuples = [(key, self.imageDict[key]) for key in self.imageDict]
        self.imageDict = OrderedDict(sorted(tuples, key=lambda x: len(x[1]), reverse=False))
        self.iterator = iter(self.imageDict)
        self.hasChanged.set(False)

    def showNextImage(self):
        #reorder dict by amount of labels to show unfinished images first, but only if user has changed something to prevent alternating
        if self.hasChanged.get():
            self.sortDict()

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

                #load label values if applicable
                if "signalnoise" in self.imageDict[self.currentkey]:
                    self.signalnoise.set(self.imageDict[self.currentkey]["signal"])
                if "confidence" in self.imageDict[self.currentkey]:
                    self.confidence.set(self.imageDict[self.currentkey]["confidence"])
                #TODO: update radiobuttons
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
            self.imageDict[self.currentkey]["signal"] = self.signalnoise.get()
            out_file = open(self.dir.get() + "/labels.json", 'w')
            json.dump(self.imageDict, out_file)
            out_file.close()
        self.destroy()

    def change(self):
        self.hasChanged.set(True)

    def updateInfoString(self):
        if self.dir.get() == "":
            infoString = "No Directory Selected"
        else:
            imagecount = len([f for f in os.listdir(self.dir.get()) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.gif')])
            infoString = "Directory: " + self.dir.get() + ", Images: " + str(imagecount)
        return infoString

    def __init__(self):
        super().__init__()
        self.title("Labeler")
        self.geometry("1536x864")
        self.configure(background="white")

        self.dir = tk.StringVar()
        self.dir.set("")
        self.dir.trace('w', self.loadImages)
        self.signalnoise = tk.BooleanVar()
        self.confidence = tk.IntVar()
        self.imageDict = {}
        self.imagePilList = []
        self.currentkey = ""
        self.hasChanged = tk.BooleanVar()
        self.hasChanged.set(True)
        self.infoString = self.updateInfoString()


        self.columnconfigure(0, weight=3, uniform='column')
        self.columnconfigure(1, weight=1, uniform='column')
        self.rowconfigure(0, weight=1, uniform='row')

        self.label_frame = tk.Frame(self)
        self.label_frame.grid(column=1, row=0)
        self.label_frame.configure(background="white")


        self.dirButton = tk.Button(self.label_frame, text="Select Image Directory", command=self.selectDir)
        self.dirinfo = tk.Label(self.label_frame, text=self.infoString)

        self.signalbutton = tk.Radiobutton(self.label_frame, text="Signal", variable=self.signalnoise, value=True, command=self.change)
        self.noisebutton = tk.Radiobutton(self.label_frame, text="Noise", variable=self.signalnoise, value=False, command=self.change)

        self.conf1 = tk.Radiobutton(self.label_frame, text="1", variable=self.confidence, value=1, command=self.change)
        self.conf2 = tk.Radiobutton(self.label_frame, text="2", variable=self.confidence, value=2, command=self.change)
        self.conf3 = tk.Radiobutton(self.label_frame, text="3", variable=self.confidence, value=3, command=self.change)

        self.savebutton = tk.Button(self.label_frame, text="Next", command=self.save)
        self.exitbutton = tk.Button(self.label_frame, text="Save & Exit", command=self.saveexit)

        self.dirButton.pack(side='top', pady=15)
        self.dirinfo.pack(side='top', pady = 0)
        self.signalbutton.pack(side='top', pady=15)
        self.noisebutton.pack(side='top', pady=15)

        self.conf1.pack(side='top', pady=3)
        self.conf2.pack(side='top',  pady=3)
        self.conf3.pack(side='top',  pady=3)
        self.savebutton.pack(side='top', pady=15)
        self.exitbutton.pack(side='top', pady=15)


        #self.dirButton.grid(column=1, row=0)
        #self.signalbutton.grid(column=1, row=0)
        #self.noisebutton.grid(column=1, row=0)
        #self.conf1.grid(column=1, row=0)
        #self.conf2.grid(column=1, row=0)
        #self.conf3.grid(column=1, row=0)
        #self.savebutton.grid(column=1, row=0)
        #self.exitbutton.grid(column=1, row=0)

        self.defaultImage = Image.open("defaultImage.png")

        self.defaultImage = ImageTk.PhotoImage(self.defaultImage.resize((800, 500)))
        self.imageLabel = tk.Label(self, image=self.defaultImage, bg="blue4")
        self.imageLabel.image = self.defaultImage
        self.imageLabel.grid(column=0, row=0)








if __name__ == '__main__':
    self = Labeler()
    self.mainloop()


#Missing functionality:

#layouting

