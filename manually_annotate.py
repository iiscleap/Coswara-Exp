#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:02:50 2020

@author: shreyasr
"""

import os
import sys
import numpy as np
import subprocess
import pandas as pd
from pdb import set_trace as bp

# from playsound import playsound
# """
# In case playsound doesn't work:

def playsound(f):
    subprocess.Popen("aplay {} 2>/dev/null >/dev/null".format(f), shell=True)    
    # Or use anything else to play
# """
def getUserInput(question, uttid):
    finish=False
    try:
        a = input(question.format(uttid))
    except KeyboardInterrupt:
        a = 'exit'
        fin = input("Sure you want to exit? (y/n) :")
        if fin == 'y':
            finish = input("Save Progress? (y/n) :")=='y'
            if not finish:
                sys.exit()
    return a, finish

def saveProgress(finish, responses, annot_csvfile, utt2annotator, anotator_dict, done_dict):
    if finish:
        responses = pd.DataFrame(np.asarray(responses[:-1])).to_csv(index=None,header=None)
        with open(annot_csvfile,'a+') as f:
            f.write(responses)
        write_utt2annotator(utt2annotator, anotator_dict, done_dict) 
        sys.exit()
        
        
def load_annotator_info(utt2annotator):
    annotatorcsv = np.genfromtxt(utt2annotator,dtype='str',delimiter=',', skip_header=1)
    anotator_dict = dict(zip(annotatorcsv[:,0],annotatorcsv[:,1]))
    done_dict = dict(zip(annotatorcsv[:,0],annotatorcsv[:,2]))
    return annotatorcsv, anotator_dict, done_dict

def get_uttids_to_annotate(wavscp, existing_uttids_in_annot, anotator_dict):
    n_utts = int(input("How many utterances will you annotate now? :"))
    utts = []
    i = 0
    for uttid in wavscp[:,0]:
        if uttid not in existing_uttids_in_annot:
            if uttid not in anotator_dict.keys():
                i+=1
                if i>n_utts:
                    break
                utts.append(uttid)
    return utts

def write_utt2annotator(utt2annotator, anotator_dict, done_dict):
    a = np.asarray([[utt, a, done_dict[utt]] for utt,a in anotator_dict.items()])
    np.savetxt(utt2annotator,a,fmt='%s',delimiter=',',comments='',header='uttid,annotator,done')
    
def main():
    wavscp = np.genfromtxt('data/wav.scp', dtype='str')
    annot_csvfile = 'data/annot.csv'
    utt2annotator = 'data/utt2annotator'
    if os.path.exists(annot_csvfile):
        existing_uttids_in_annot = np.genfromtxt(annot_csvfile, dtype='str',delimiter=',').T[0][1:]
    else:
        raise("Check annot csv file path")
    
    if os.path.exists(utt2annotator):
        annotatorcsv, anotator_dict, done_dict = load_annotator_info(utt2annotator)
    else:
        raise("Check utt2annotator path!")

    annotator = input("Who is annotating? : ")
    remaining_utts_idx  = (annotatorcsv[:,1]==annotator)*(annotatorcsv[:,2]=='n')
    remaining_utts = annotatorcsv[:,0][remaining_utts_idx]
    if remaining_utts.size == 0:
        remaining_utts = get_uttids_to_annotate(wavscp, existing_uttids_in_annot, anotator_dict)
        anotator_dict.update(dict(zip(remaining_utts,[annotator for u in remaining_utts])))
        done_dict.update(dict(zip(remaining_utts,['n' for u in remaining_utts])))
        write_utt2annotator(utt2annotator, anotator_dict, done_dict)
        
    
    questions = ["Is audio present? (y/n) : ",
                 "Is the file clean? (y/n) : ",
                 "Is the audio contiuous (not breaking in between)? (y/n) :",
                 "Is the volume OK? (y/n) : ",
                 "Is the audio category matching with uttid {}? (y/n) : ",
                 "Which category does the audio actually belong? \
                     Breathing-Shallow (1), Breathing-Deep (2), Cough-Shallow (3),\n\
                      Cough-Heavy (4), A sound (5), E sound (6), \n\
                          oo Sound (7), Counting fast (8), Counting slow (9),\n\
                              None of these/Correct Category (default):"]
    
    expected_responses = [["y","n"], ["y","n"], ["y","n"], ["y","n"], ["y","n"],
                          list(np.arange(1,10).astype(str))+[""]]
    
    responses = []
    
    for uttid, wavfile in wavscp:
        if uttid in existing_uttids_in_annot:
            continue
        if uttid not in anotator_dict.keys():
            continue
        if anotator_dict[uttid]!=annotator:
            continue
        responses.append([uttid])
        print("Playing {}:".format(uttid))
        playsound(wavfile)
        print("{}:".format(uttid))
        for question, expected in zip(questions, expected_responses):
            while(True):
                a, finish = getUserInput(question, uttid)
                if a in expected:
                    responses[-1].append(a)
                    break
                elif a == "exit":
                    finish=True
                    break
                elif a == "p": #Play again
                    playsound(wavfile)
                else:
                    print("Invalid Input. Try again \n")
            saveProgress(finish, responses, annot_csvfile, utt2annotator, anotator_dict, done_dict)
        a, finish = getUserInput("Any other comments?", uttid)
        done_dict[uttid]='y'
        saveProgress(finish, responses, annot_csvfile, utt2annotator, anotator_dict, done_dict)
        responses[-1].append(a.replace(',','.'))
    
    responses = pd.DataFrame(np.asarray(responses)).to_csv(index=None,header=None)
    with open(annot_csvfile,'a+') as f:
        f.write(responses)
    write_utt2annotator(utt2annotator, anotator_dict, done_dict)
    print("Done annotating files assigned to {}.".format(annotator))
    a = np.genfromtxt(annot_csvfile, dtype='str',delimiter=',').T[0][1:]
    b = np.genfromtxt('data/wav.scp',dtype='str')
    print("Total utts = {}\nUtts annotated = {}\nRemaining = {}".format(len(b),len(a),len(b)-len(a)))
            
if __name__=='__main__':
    main()
