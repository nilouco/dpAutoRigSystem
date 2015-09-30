import logging as _logging
logging = _logging.getLogger()
logging.setLevel(_logging.WARNING)
import sys

import os
import json
#import yaml

_complex_types = [dict]
def _isDataComplex(_data):
    return any(filter(lambda x: isinstance(_data, x), (iter(_basic_types)))) or hasattr(_data, '__dict__')

_basic_types = [int, float, basestring, bool]
def _isDataBasic(_data):
    global _basic_types
    return any(filter(lambda x: isinstance(_data, x), (iter(_basic_types))))

_list_types = [list, tuple]
def _isDataList(_data):
    global _list_types
    return any(filter(lambda x: isinstance(_data, x), (iter(_list_types))))

_dag_types = []
def _isDataDagNode(_data):
    global _dag_types
    return any(filter(lambda x: isinstance(_data, x), iter(_dag_types)))


# constants
TYPE_BASIC, TYPE_LIST, TYPE_DAGNODE, TYPE_COMPLEX = range(4)

def get_class_def(_clsName, _baseclass=object):
    try:
        for cls in _baseclass.__subclasses__():
            if cls.__name__ == _clsName:
                return cls
            else:
                t = get_class_def(_clsName, _baseclass=cls)
                if t is not None:
                    return t
    except Exception, e:
        pass #logging.info(str(e)) # TODO: FIX
    return None

def create_class_instance(_clsName):
    cls = get_class_def(_clsName)

    if cls is None:
        logging.warning("Can't find class definition '{0}'".format(_clsName));
        return None

    clsDef = getattr(sys.modules[cls.__module__], cls.__name__)
    assert(clsDef is not None)

    try:
        return clsDef()
    except Exception, e:
        logging.error("Fatal error creating '{0}' instance: {1}".format(_clsName, str(e)))
        return None

def get_class_namespace(_cls):
    if not isinstance(_cls, object):
        return None # Todo: throw exception
    tokens = []
    while (not _cls is object):
        tokens.append(_cls.__name__)
        _cls = _cls.__bases__[0]
    return '.'.join(reversed(tokens))

#
# Types definitions
# Type affect how the data is read & writen.
# By using global variables, we allow any script to hook itself in the module.
#

# We consider a data complex if it's a class instance.
# Note: We check for __dict__ because isinstance(_data, object) return True for basic types.
_complex_types = [dict]
def _isDataComplex(_data):
    return any(filter(lambda x: isinstance(_data, x), (iter(_basic_types)))) or hasattr(_data, '__dict__')

_basic_types = [int, float, basestring, bool]
def _isDataBasic(_data):
    global _basic_types
    return any(filter(lambda x: isinstance(_data, x), (iter(_basic_types))))

_list_types = [list, tuple]
def _isDataList(_data):
    global _list_types
    return any(filter(lambda x: isinstance(_data, x), (iter(_list_types))))

_dag_types = []
def _isDataDagNode(_data):
    global _dag_types
    return any(filter(lambda x: isinstance(_data, x), iter(_dag_types)))


__types__ = {
    TYPE_LIST: _isDataList,
    TYPE_BASIC: _isDataBasic,
    TYPE_DAGNODE: _isDataDagNode,
    TYPE_COMPLEX: _isDataComplex
}
def getDataType(_data, *args, **kwargs):
    for type_id, type_fn in __types__.iteritems():
        if type_fn(_data):
            return type_id

    '''
    if _isDataList(_data, *args, **kwargs):
        return TYPE_LIST
    elif _isDataBasic(_data, *args, **kwargs):
        return TYPE_BASIC
    elif _isDataDagNode(_data, *args, **kwargs):
        return TYPE_DAGNODE
    elif _isDataComplex(_data, *args, **kwargs):
        return TYPE_COMPLEX
    else:
        logging.warning('{0} is unknow type'.format(_data))
    '''

    logging.warning('{0} is unknow type'.format(_data))



def _export_basicData(_data, _bSkipNone=True, _bRecursive=True, **args):
    ##logging.debug('[exportToBasicData]', _data)

    sType = getDataType(_data)
    # object instance
    if sType == TYPE_COMPLEX:
        dicReturn = {}
        dicReturn['_class'] = get_class_namespace(_data.__class__)
        dicReturn['_uid'] = id(_data)
        for key, val in (_data.items() if isinstance(_data, dict) else _data.__dict__.items()): # TODO: Clean
            if '_' not in key[0]:
                if not _bSkipNone or val is not None:
                    if (sType == TYPE_COMPLEX and _bRecursive is True) or sType == TYPE_LIST:
                        val = _export_basicData(val, _bSkipNone=_bSkipNone, _bRecursive=_bRecursive, **args)
                    if not _bSkipNone or val is not None:
                        dicReturn[key] = val

        return dicReturn

    # Handle other types of data
    elif sType == TYPE_BASIC:
        return _data

    # Handle iterable
    elif sType == TYPE_LIST:
        return [_export_basicData(v, _bSkipNone=_bSkipNone, **args) for v in _data if not _bSkipNone or v is not None]

    elif sType == TYPE_DAGNODE:
        return _data

    logging.warning("[exportToBasicData] Unsupported type {0} ({1}) for {2}".format(type(_data), sType, _data))
    return None


def _import_basicData(_data, **args):
    assert(_data is not None)
    if isinstance(_data, dict) and '_class' in _data:
        # Handle Serializable object
        clsPath = _data['_class']
        clsName = clsPath.split('.')[-1]
        instance = create_class_instance(clsName)
        if instance is None or not isinstance(instance, object):
            logging.error("Can't create class instance for {0}, did you import to module?".format(clsPath))
            # TODO: Log error
            return None
        for key, val in _data.items():
            if key != '_class':
                instance.__dict__[key] = _import_basicData(val, **args)
        return instance
    # Handle array
    elif _isDataList(_data):
        return [_import_basicData(v, **args) for v in _data]
    # Handle other types of data
    else:
        return _data

#
# Json Support
#

def _handle_dir_creation(path):
    path_dir = os.path.dirname(path)

    # Create destination folder if needed
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

def export_json(data, **kwargs):
    dicData = _export_basicData(data)
    return json.dumps(data, **kwargs)

def export_json_file(data, path, mkdir=True, **kwargs):
    if mkdir: _handle_dir_creation(path)

    dicData = _export_basicData(data)

    with open(path, 'w') as fp:
        json.dump(dicData, fp, **kwargs)

    return True

def import_json(str_, **kwargs):
    dicData = json.loads(str_, **kwargs)
    return _import_basicData(dicData)

def import_json_file(path, **kwargs):
    if not os.path.exists(path):
        raise Exception("Can't importFromJsonFile, file does not exist! {0}".format(path))

    with open(path, 'r') as fp:
        dicData = json.load(fp, **kwargs)
        return _import_basicData(dicData)

#
# Yaml support
#

#def export_yaml(data, **kwargs):
#    dicData = _export_basicData(data)
#    return yaml.dump(dicData, **kwargs)

#def export_yaml_file(data, path, mkdir=True, **kwargs):
#    if mkdir: _handle_dir_creation(path)

#    dicData = _export_basicData(data)

#    with open(path, 'w') as fp:
#        yaml.dump(dicData, fp)

#    return True

#def import_yaml(str_, **kwargs):
#    dicData = yaml.load(str_)
#    return _import_basicData(dicData)

#def import_yaml_file(path, **kwargs):
#    if not os.path.exists(path):
#        raise Exception("Can't importFromYamlFile, file does not exist! {0}".format(path))

#    with open(path, 'r') as fp:
#        dicData = yaml.load(fp)
#        return _import_basicData(dicData)
