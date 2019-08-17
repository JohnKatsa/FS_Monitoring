import os

def makeFilesMap(curr_dir):
    myMap = {}

    for root, dirs, files in os.walk(curr_dir, topdown=False):
        for name in files:
            if os.path.isfile(os.path.join(root, name)):
                #print(os.path.join(root, name), "with size:", os.path.getsize(os.path.join(root, name)))
                myMap[os.path.join(root, name)] = os.path.getsize(os.path.join(root, name))

    return myMap