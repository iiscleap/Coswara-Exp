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

def saveProgress(finish, responses, annot_csvfile):
    if finish:
        responses = pd.DataFrame(np.asarray(responses[:-1])).to_csv(index=None,header=None)
        with open(annot_csvfile,'a+') as f:
            f.write(responses)
        sys.exit()

def main():
    wavscp = np.genfromtxt('data/wav.scp', dtype='str')
    annot_csvfile = 'data/annot.csv'
    
    if os.path.exists(annot_csvfile):
        existing_uttids_in_annot = np.genfromtxt(annot_csvfile, dtype='str',delimiter=',').T[0]
    else:
        with open(annot_csvfile,'w') as f:
            f.write("UttId,q1,q2,q3,q4,q5,q6,OtherComments\n")
        existing_uttids_in_annot = []
    
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
            saveProgress(finish, responses, annot_csvfile)
        a, finish = getUserInput("Any other comments?", uttid)
        saveProgress(finish, responses, annot_csvfile)
        responses[-1].append(a.replace(',','.'))
    
    responses = pd.DataFrame(np.asarray(responses)).to_csv(index=None,header=None)
    with open(annot_csvfile,'a+') as f:
        f.write(responses)
            
            
if __name__=='__main__':
    main()
