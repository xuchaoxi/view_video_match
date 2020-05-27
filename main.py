import web
import os, sys, random
import json
import numpy as np

from images import images

urls = (
    '/', 'index',
    '/search', 'ImageSearch',
    '/images/(.*)', 'images',
    '/img/(.*)', 'images',
)
       
render = web.template.render('templates/')

pwd = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(os.path.join(pwd,'config.json')))

cap_method = os.path.join(config['automatch'], config['model_config'])
max_hits = config['max_hits']
metric = config['metric']
collection = config['collection']
text_set = config['text_set']


def generate_query_results(hitlist):
    num = len(hitlist)
    name2index = dict(zip(hitlist, range(num)))
    content = [None] * num

    for shot in hitlist:
        res = {'shot': shot, 'img': web.shot2imgs[shot][0], 'color': 'white'}
        content[name2index[shot]] = res

    return content


def generate_shot_images(hitlist):

    hitlist = sorted(hitlist, key=lambda x : int(x.rsplit('_',1)[1]))
    num = len(hitlist)
    name2index = dict(zip(hitlist, range(num)))
    content = [None] * num
    for img in hitlist:
        res = {'shot': img.rsplit('_', 1)[0], 'img': img, 'color': 'white' }
        content[name2index[img]] = res

    return content

class index:
    
    def GET(self):
        input = web.input(query=None)
        resp = {'sent':'', 'status':0, 'query':'', 'hits':0, 'results':[], 
                    'metric':metric, 'perf':0, 'collection':collection}

        if input.query:
            resp['status'] = 1
            resp['query'] = input.query
            if resp['query'].startswith('shot2images-'):
                query = resp['query'].strip().split('shot2images-')[-1]
                resp['query'] = query
                hitlist = web.shot2imgs[query][:max_hits]
                resp['results'] = generate_shot_images(hitlist)
            else:
                query = input.query.lower().split()[0]

                hitlist = web.sent2shot[query][:max_hits]
                resp['results'] = generate_query_results(hitlist)
            
        else:
            hitlist = web.txts[:max_hits] #random.sample(web.txts, min(max_hits, len(web.txts)))
            resp['results'] = hitlist

        resp['hits'] = len(hitlist)
        return render.index(resp)

class ImageSearch:
    def POST(self):
        input = web.input()
        raise web.seeother('/?query=%s' % input.tags)


        
if __name__ == "__main__":
    app = web.application(urls, globals())

    rootpath = os.path.join(os.environ['HOME'], 'VisualSearch')

    txt_file = os.path.join(rootpath, collection, 'TextData', text_set)
    web.txts = map(str.strip, open(txt_file).readlines())

    resfile = os.path.join(rootpath, collection, cap_method, 'id.sent.score.txt')
    sent2shot = {}
    for line in open(resfile):
        elems = line.strip().split()
        sent_id = elems[0]
        del elems[0]
        assert len(elems) % 2 == 0
        shots = [elems[i] for i in range(0, max_hits*2, 2)]
        sent2shot[sent_id] = shots

    web.sent2shot = sent2shot

    shot2imgs = {}
    imset = os.path.join(rootpath, collection, 'ImageSets', collection+'.txt')
    for line in open(imset):
        shotid, imageid = line.strip().rsplit('_', 1)[0], line.strip()
        shot2imgs.setdefault(shotid, []).append(imageid)
    web.shot2imgs = shot2imgs

    app.run()
