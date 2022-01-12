#!/usr/bin/env python
from tqdm import tqdm
import pandas as pd
import optparse
import os
from glob import glob
import parse_es_senseval as ps

def find_files(_basepath,ext='*.train.tagged.xml'):
    filelist = [file for file in glob(os.path.join(_basepath,'**',ext))]
    if not filelist:
        filelist = [file for file in glob(os.path.join(_basepath,ext))]
    if not filelist:
        error_msg = 'Did not find any training files with {}'.format(ext)
        error_msg+= ' extension in folder {}'.format(_basepath)
        raise FileNotFoundError(error_msg)
    return filelist[0]



def build_joint_train_es_senseval_gloss_corpus(_basepath,verbose=True):
    """
    Given filepath to base folder of semseval 3 spanish corpus containing the xml.gz files
    Parses corpus and generates joint context-gloss pairs from wordnet glosses  """

    _train_corpus_fileref = find_files(_basepath,'*.train.tagged.xml')
    _dict_fileref = find_files(_basepath,'MiniDir.xml')
       
    if verbose: print('Parsing training corpus')
    _train_senseval_corpus_df = ps.parse_es_senseval3_corpus_xml(_train_corpus_fileref)
    if verbose: print('Parsing dictionary')
    
    _senseval_dict_df = ps.parse_es_senseval3_dict_xml(_dict_fileref)
       
    if verbose: print('Building joint training corpus')
    _joint_train_corpus_df= pd.merge(_train_senseval_corpus_df,_senseval_dict_df,on='target_word',suffixes=['','_dict'])
    _joint_train_corpus_df.loc[:,'is_proper_gloss'] = _joint_train_corpus_df['sense_id']==_joint_train_corpus_df['sense_id_dict']

      
    return _joint_train_corpus_df.drop(columns=['sense_id_dict','used'])


def build_joint_test_es_senseval_gloss_corpus(_basepath,verbose=True):
    """
    Given filepath to base folder of semseval 3 spanish corpus containing the xml.gz files
    Parses corpus and generates joint context-gloss pairs from wordnet glosses  """


    _dict_fileref = find_files(_basepath,'MiniDir.xml')
    _test_corpus_fileref = find_files(_basepath,'*.test.tagged.xml')
    _test_key_file = find_files(_basepath,'*.test.key')
        
    if verbose: print('Parsing dictionary')
    _senseval_dict_df = ps.parse_es_senseval3_dict_xml(_dict_fileref)
       
    if verbose: print('Parsing Testing corpus')
    _test_senseval_corpus_df = ps.parse_es_senseval3_corpus_xml(_test_corpus_fileref)
    if verbose: print('Parsing test sense key file')
    _test_key_df = ps.parse_es_senseval3_sense_tags(_test_key_file)
    if verbose: print('Adding test sense keys to test file')
    _labeled_test_df = pd.merge(_test_senseval_corpus_df,_test_key_df[['ref','sense_id']],on='ref',suffixes=['','_tagged'])
    _labeled_test_df.loc[:,'sense_id'] = _labeled_test_df['sense_id_tagged']
    _labeled_test_df = _labeled_test_df.drop(columns='sense_id_tagged',axis=1)

    if verbose: print('Building joint training corpus')
    _joint_test_corpus_df= pd.merge(_labeled_test_df,_senseval_dict_df,on='target_word',suffixes=['','_dict'])
    _joint_test_corpus_df.loc[:,'is_proper_gloss'] = _joint_test_corpus_df['sense_id']==_joint_test_corpus_df['sense_id_dict']
    
    return _joint_test_corpus_df.drop(columns=['sense_id_dict','used'])


def build_joint_es_senseval_gloss_corpus(_basepath,verbose=True):
    """
    Given filepath to base folder of semseval 3 spanish corpus containing the xml.gz files
    Parses corpus and generates joint context-gloss pairs from wordnet glosses  """

    _joint_train_corpus_df = build_joint_train_es_senseval_gloss_corpus(_basepath,verbose=verbose)
    _joint_test_corpus_df = build_joint_test_es_senseval_gloss_corpus(_basepath,verbose=verbose)
    
    return _joint_train_corpus_df,_joint_test_corpus_df 



if  __name__ == '__main__':
    from argparse import ArgumentParser
    import os

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = ArgumentParser(description='Process some integers.')
    parser.add_argument('--fpath',  type=str, default='./data/raw/',
                       help='File path to the semcor directory')   
    parser.add_argument('--savepath_train',  type=str, default='./data/preprocessed/senseval_es_train_gloss.feather',
                       help='save path to final train senseval directory')
    parser.add_argument('--savepath_test',  type=str, default='./data/preprocessed/senseval_es_test_gloss.feather',
                       help='save path to final test senseval directory')
    args = parser.parse_args()
    print(args)
    print()
    train_corpus, test_corpus = build_joint_es_senseval_gloss_corpus(args.fpath)
    train_corpus.to_feather(args.savepath_train)
    test_corpus.to_feather(args.savepath_test)
