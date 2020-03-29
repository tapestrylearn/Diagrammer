from . import model

from django.contrib.sessions.serializers import JSONSerializer


class DiagrammerJSONSerializer(JSONSerializer):
    def dumps(self, obj: object) -> 'data':
        try:
            return JSONSerializer.dumps(self, obj)
        except TypeError:
            if type(obj) in model.TYPES:
                return JSONSerializer.dumps(self, obj.export())
    
    
    def loads(self, data: 'data') -> object:
        raw_dict = JSONSerializer.loads(self, data)

        for model_type in model.TYPES:
            try:
                return model_type.from_json(raw_dict)
            except KeyError:
                continue
            
        return raw_dict