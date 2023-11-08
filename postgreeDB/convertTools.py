

import json

## postgreslq 은 공백처리 상관없는데 
## 타 DB json null로 나올경 우 공백으로 대체 
class NoneToEmptyJSON(json.JSONEncoder):
    def default(self, o):

        
        if o == None:
            o = ''
        elif type(o) == dict:
            return {self.default(key): self.default(value) for key, value in o.items()}
        elif type(o) == list or type(o) == tuple:
            return [self.default(item) for item in o]
        return o
    def encode(self, o):
        return super().encode(self.default(o))
    

def convert_null_to_blank(data):
        if isinstance(data, dict):
            return {k: convert_null_to_blank(v) if v is not None else '' for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_null_to_blank(item) if item is not None else '' for item in data]
        else:
            return data    
        

def find_matching_indexes(array, value):
    indexes = []  # 일치하는 인덱스를 저장할 리스트

    for i in range(len(array)):
        if array[i] == value:
            indexes.append(i)

    return indexes
