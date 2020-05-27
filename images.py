import sys
import web
import os
import json


ROOT_PATH=os.path.join(os.environ['HOME'], 'VisualSearch')

cType = {".png":"images/png",
         ".jpg":"images/jpeg",
         ".jpeg":"images/jpeg",
         ".gif":"images/gif",
         ".ico":"images/x-icon"}


pwd = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(os.path.join(pwd,'config.json')))

collection=config['collection']

id2path = dict([line.strip().split() for line in 
                open(os.path.join(ROOT_PATH, collection, 'id.imagepath.txt'))])

def im2path(name, rootpath=ROOT_PATH):
    collection, imageid = name.rsplit('-', 1)
    imageid = imageid.rsplit('.', 1)[0]
    imfile = id2path[imageid]

    return imfile

class images:
    def get_local(self, name):
        return im2path(name)

    def GET(self,name):
        imfile = self.get_local(name)
        try:
            web.header("Content-Type", cType[os.path.splitext(imfile)[1]]) # Set the Header
            return open(imfile,"rb").read() # Notice 'rb' for reading images
        except Exception, e:
            print (e)
            raise web.notfound()

class queryimages (images):
    def get_local(self, name):
        return im2path(name)
            
