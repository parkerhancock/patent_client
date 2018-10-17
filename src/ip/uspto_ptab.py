import requests
import json
from copy import deepcopy
from ip import CACHE_BASE
from ip.util import BaseSet, hash_dict
import inflection
import mimetypes
import os
import shutil
from dateutil.parser import parse as parse_dt

CACHE_DIR = CACHE_BASE / 'ptab'
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()

class PtabManager(BaseSet):
    page_size = 25

    def __init__(self, *args, **kwargs):
        self.args = args 
        self.kwargs = kwargs
        self.obj_class = globals().get(self.obj_class)
    
    def filter(self, *args, **kwargs):
        return self.__class__(*args, *self.args, **{**kwargs, **self.kwargs})
    
    def get(self, *args, **kwargs):
        manager = self.filter(*args, **kwargs)
        count = manager.count()
        if count > 1:
            raise ValueError('More than one result!')
        elif count == 0:
            raise ValueError('Object Not Found!')
        else:
            return manager.first()

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            offset = int(key / self.page_size) * self.page_size
            position = (key % self.page_size)
            data = self.request(dict(offset=offset))
            results = data['results']
            return self.obj_class(results[position])
    
    def order_by(self, *args):
        kwargs = deepcopy(self.kwargs)
        if 'sort' not in kwargs:
            kwargs['sort'] = list()
        kwargs['sort'] += args
        return self.__class__(*self.args, **kwargs)


    def first(self):
        data = self.request()
        return self.obj_class(data['results'][0])

    def __len__(self):
        return self.count()

    def count(self):
        response = self.request()
        response_data = response
        count = response_data['metadata']['count']
        return count
        
    def request(self, params=dict()):
        params = {**{self.primary_key: self.args}, **self.kwargs, **params}
        params = {inflection.camelize(k, uppercase_first_letter=False): v for (k, v) in params.items()}
        fname = CACHE_DIR / f'{self.__class__}-{hash_dict(params)}.json'
        if not fname.exists():
            response = session.get(self.base_url, params=params)
            with open(fname, 'w') as f:
                json.dump(response.json(), f, indent=True)
        return json.load(open(fname))

    def all(self):
        length = self.count()
        offset = 0
        while offset < length:
            response = self.request(dict(offset=offset))
            results = response['results']
            for result in results:
                yield self.obj_class(r)
            offset += self.page_size

class PtabObject:
    def __init__(self, data):
        self.dict = {inflection.underscore(k): v for (k, v) in data.items()}
        for k, v in self.dict.items():
            if 'datetime' in k:
                self.dict[k] = parse_dt(v)
            elif 'date' in k:
                self.dict[k] = parse_dt(v).date()
            setattr(self, k, self.dict[k])

class PtabTrialManager(PtabManager):
    base_url = 'https://ptabdata.uspto.gov/ptab-api/trials'
    obj_class = 'PtabTrial'
    primary_key = 'trial_number'

class PtabTrial(PtabObject):
    objects = PtabTrialManager()

    def __repr__(self):
        return f'<PtabTrial(trial_number={self.trial_number})>'
    
    @property
    def documents(self):
        return PtabDocument.objects.filter(trial_number=self.trial_number)
        
class PtabDocumentManager(PtabManager):
    base_url = 'https://ptabdata.uspto.gov/ptab-api/documents'
    obj_class = 'PtabDocument'
    primary_key = 'id'

    

class PtabDocument(PtabObject):
    objects = PtabDocumentManager()

    @property
    def trial(self):
        return PtabTrial.objects.get(self.trial_number)
    
    def download(self, path='.'):
        url = self.links[1]['href']
        extension = mimetypes.guess_extension(self.media_type)
        base_name = self.title.replace('/', '_') + extension
        cdir = os.path.join(CACHE_DIR, self.trial_number)
        os.makedirs(cdir, exist_ok=True)
        cname = os.path.join(cdir, base_name)
        oname = os.path.join(path, base_name)
        if not os.path.exists(cname):
            response = session.get(url, stream=True)
            with open(cname, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        shutil.copy(cname, oname)

    def __repr__(self):
        return f'<PtabDocument>'

