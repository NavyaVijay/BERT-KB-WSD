import pandas as pd
import gzip
import os
import xml.etree.ElementTree as ET


def xml_parse_senseval3_corpus(_xmlfile):
    _dct_list = []
    sctree = ET.parse(_xmlfile)
    # Iterates over list of words in files    
    dct_list1 = []
    for node in sctree.iter('instance'):
        attributes = node.attrib
        sid = 0
        if node.find('answer') is not None:
            sid = node.find('answer').attrib['senseid'].split('.')[1]   

        ctx = node.find('context/target')
        head = ctx.text.strip("\n")
        target = ctx.find('head').text.strip('\n')
        tail = ctx.find('head').tail.strip('\n').strip(' ')
        sentence = head+target+tail
        _dct_list.append({'ref':attributes['id'],'sense_id':sid,
                            'context':sentence,'target_word':target})
    return _dct_list

def xml_parse_senseval2_corpus(_xmlfile):
    sctree = ET.parse(_xmlfile)
    # Iterates over list of words in files    
    _dct_list = []
    for node in sctree.iter('instance'):
        attributes = node.attrib
        sid = 0
        if node.find('answer') is not None:
            #sid = node.find('answer').attrib['senseid'].split('.')[1]  
            sid = node.find('answer').attrib['senseid']

        ctx = node.find('context')
        head = ctx.text.strip("\n")
        target = ctx.find('head').text.strip('\n')
        tail = ctx.find('head').tail.strip('\n').strip(' ')
        sentence = head+target+tail
        sentence = head+target+tail
        _dct_list.append({'ref':attributes['id'],'sense_id':sid,
                         'context':sentence,'target_word':target})
        _dct_list
    return _dct_list


def parse_es_senseval3_corpus_xml(_fpath):
    """
    Parses semeval spanish word train dataset 
    (input file in xml.gz or xml format), on the train dataset returns
    senseid 0 since the latter is not tagged
    warning ISO encoding is buggy with spanish caracters, works
    better with gz files         
    """
    
    _, file_extension = os.path.split(os.path.splitext(_fpath)[1])    

    dct_list = []
    if file_extension == '.gz':
        with gzip.open(_fpath) as xmlfile:
            dct_list = xml_parse_senseval3_corpus(xmlfile)
    elif file_extension == '.xml':
        #with open(_fpath,'r',encoding = "ISO-8859-1") as xmlfile:
        with open(_fpath,'r',encoding="ISO-8859-1") as xmlfile:
            dct_list = xml_parse_senseval3_corpus(xmlfile)
    else:
        raise IOError('Not a xml.gz or xml file')        

    return pd.DataFrame(dct_list)

def parse_es_senseval2_corpus_xml(_fpath):
    """
    Parses semeval spanish word train dataset 
    (input file in xml.gz or xml format), on the train dataset returns
    senseid 0 since the latter is not tagged
    warning ISO encoding is buggy with spanish caracters, works
    better with gz files         
    """
    
    _, file_extension = os.path.split(os.path.splitext(_fpath)[1])    

    dct_list = []
    if file_extension == '.gz':
        with gzip.open(_fpath) as xmlfile:
            dct_list = xml_parse_senseval2_corpus(xmlfile)
    elif file_extension == '.xml':
        #with open(_fpath,'r',encoding = "ISO-8859-1") as xmlfile:
        #with open(_fpath,'r',encoding="ISO-8859-1") as xmlfile:
        with open(_fpath,'r',encoding="ISO-8859-1") as xmlfile:
            dct_list = xml_parse_senseval2_corpus(xmlfile)
    else:
        raise IOError('Not a xml.gz or xml file')        

    return pd.DataFrame(dct_list)

   
def parse_es_senseval3_dict_xml(_fpath):
    """
    Parses semeval spanish word dicitonary dataset
    
    """
    dicttree = ET.parse(_fpath)
    # Iterates over list of words in files    
    dct_list = []
    for node in dicttree.iter('sense'):
        attributes = node.attrib
        sid = attributes['id'].split('.')
        gloss = attributes['definition']
        dct_list.append({'sense_id':sid[1],'gloss':gloss,'target_word':sid[0],'used':attributes['used']})
    return pd.DataFrame(dct_list)


def parse_es_senseval3_sense_tags(_fpath):
    """
    Given path to sense tags returns pandas dataframe with senseval context reference and sense id
    """
    _sense_df = pd.read_csv(_fpath,sep='\s',header=None,names=['target_word','ref','sense_id'])
    _sense_df.loc[:,'target_word'] = _sense_df['target_word'].apply(lambda x: x.split('.')[0])
    _sense_df.loc[:,'sense_id'] = _sense_df['sense_id'].apply(lambda x: x.split('.')[1])
    return _sense_df


def parse_es_senseval2_sense_tags(_fpath):
    """
    Given path to sense tags returns pandas dataframe with senseval context reference and sense id
    """
    with open(fpath,'r', encoding = "ISO-8859-1") as f:
        filedump = f.readlines()

    filecontent = [line.split('#') for line in filedump if '#SIN' in line]
    _sense_df = pd.DataFrame(filecontent,columns=['target_word','class','sense_id','gloss',4,5,6,7])
    _sense_df = _sense_df.drop(columns=[4,5,6,7])
    return _sense_df
    


