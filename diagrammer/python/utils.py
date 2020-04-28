import types
import collections

# TYPE CHECKING
def is_basic_value(obj: object) -> bool:
    return not is_collection(obj) and not is_instance(obj)

class CollectionTypes:
    Option = int

    LINEAR = 0
    MAPPING = 1

    ORDERED = 2
    UNORDERED = 3

def is_collection(obj: object) -> (CollectionTypes.Option, CollectionTypes.Option):
    base_collection_types = {
        'linear' : {
            'ordered' : [list, tuple],
            'unordered' : [set],
        },

        'mapping' : {
            'ordered' : [collections.OrderedDict],
            'unordered' : [dict, types.MappingProxyType],
        }
    }

    if any(isinstance(obj, collection_type) for collection_type in base_collection_types['linear']['ordered']):
        return (CollectionTypes.LINEAR, CollectionTypes.ORDERED)
    elif any(isinstance(obj, collection_type) for collection_type in base_collection_types['linear']['unordered']):
        return (CollectionTypes.LINEAR, CollectionTypes.UNORDERED)
    elif any(isinstance(obj, collection_type) for collection_type in base_collection_types['mapping']['ordered']):
        return (CollectionTypes.MAPPING, CollectionTypes.ORDERED)
    elif any(isinstance(obj, collection_type) for collection_type in base_collection_types['mapping']['unordered']):
        return (CollectionTypes.MAPPING, CollectionTypes.ORDERED)
    else:
        return None

def is_instance(obj: object) -> bool:
    return hasattr(obj, '__dict__')