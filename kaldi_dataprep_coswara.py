#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:18:33 2020

@author: shreyasr
"""

import os
import sys
import subprocess
import numpy as np
from io import StringIO
import glob
import json
import pandas as pd

# %% Kaldi functions
Kaldi_root = '/state/partition/softwares/Kaldi_March2020/kaldi'
fix_data_dir = "{}/egs/wsj/s5/utils/fix_data_dir.sh".format(Kaldi_root)
utt2spk_to_spk2utt = "{}/egs/wsj/s5/utils/utt2spk_to_spk2utt.pl".format(Kaldi_root)

# %% Extract Remaining Data directories

coswara_data_dir = os.path.abspath('../Coswara-Data') # Local Path of iiscleap/Coswara-Data Repo
extracted_data_dir = os.path.join(coswara_data_dir, 'extracted_data') # '/home/data/Coswara'  

if not os.path.exists(coswara_data_dir):
    raise("Check the coswara dataset directory!!")

if not os.path.exists(extracted_data_dir):
    os.makedirs(extracted_data_dir)

dirs_extracted = set(map(os.path.basename,glob.glob('{}/202*'.format(extracted_data_dir))))
dirs_all = set(map(os.path.basename,glob.glob('{}/202*'.format(coswara_data_dir))))

dirs_to_extract = list(set(dirs_all) - dirs_extracted)

for d in dirs_to_extract:
    p = subprocess.Popen('cat {}/{}/*.tar.gz.* |tar -xvz -C {}/'.format(coswara_data_dir,d, extracted_data_dir), shell=True)
    p.wait()

# %% Write wav.scp, utt2spk, etc
p = subprocess.Popen('find {} -type f -name "*.wav"'.format(extracted_data_dir), shell=True, stdout=subprocess.PIPE)
out, err = p.communicate()
wavfiles = out.decode('utf-8').strip().split('\n')

uttids = []
spks = []

for l in wavfiles:
    ls = l.split('/')
    uttids.append(ls[-2]+'_'+os.path.splitext(ls[-1])[0])
    spks.append(ls[-2])

uttids = np.asarray(uttids)
spks = np.asarray(spks)

if not os.path.exists('./data'):
    os.makedirs('./data')

np.savetxt('data/wav.scp', np.c_[uttids[:,np.newaxis], wavfiles], fmt='%s', delimiter=' ', comments='')
np.savetxt('data/utt2spk', np.c_[uttids[:,np.newaxis], wavfiles], fmt='%s', delimiter=' ', comments='')

subprocess.Popen("{} data".format(fix_data_dir))
subprocess.Popen("{} data/utt2spk > data/spk2utt".format(utt2spk_to_spk2utt))

# %% Make Metadata for all files

p = subprocess.Popen('find {} -type f -name "metadata.json"'.format(extracted_data_dir), shell=True, stdout=subprocess.PIPE)
out, err = p.communicate()
metafilenames = out.decode('utf-8').strip().split('\n')

metafiles = [json.load(open(metafile, 'r')) for metafile in metafilenames]
df = pd.DataFrame(metafiles).replace(np.nan, 'False', regex=True)
csv_content = df.to_csv(index=False)

with open('data/metadata.csv','w+') as f:
    f.write(csv_content)