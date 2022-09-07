This is a Tool for quick ICA Labelling

For Users:
 - Please write your name (I recommend first name, all lower case) in the "Username" Field before selecting the image directory, since the program will try to find and load your previous labels. If you don't have any previous labels, the program will create a new file for you.
 - The Images are not shown in alphabetical order, instead you will see unlabeled images first.
 - The "Previous" Button works only for the very last Image you rated. If this is a problem, please let me know.


For Developers:
 - ratings for each particular user are stored within the "username".json file in the image directory. If the user forgot their name, the file is named "labels.json" instead.
 - A value of -1 for a label is set as default and means the user continued without making an imput.
 - quick snippet to load the labels:

username = "labels/josefine/lisa/whatever"
 with open(self.dir.get() + "/" + username + ".json", 'r') as l:
    labels = json.load(l)

 - signal = 1 means signal, signal = 0 means noise
