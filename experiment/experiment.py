# coding=utf-8
import time
import sys
import os
import glob
import csv
import codecs
import datetime
import random
from psychopy import prefs
prefs.general['audioLib'] = ['pyo']
from psychopy import visual,event,core,gui
from fractions import Fraction
import pyaudio
import wave
import scipy.io.wavfile as wav
import numpy as np

def get_stim_info(file_name, folder):
# read stimulus information stored in same folder as file_name, with a .txt extension
# returns a list of values    
    info_file_name = os.path.join(folder, os.path.splitext(os.path.basename(file_name))[0]+'.txt')
    info = []
    with open(info_file_name,'r') as file:
        reader = csv.reader(file)
        for row in reader:
            info.append(row)
    return info

def enblock(x, n_stims):
    # generator to cut a list of stims into blocks of n_stims
    # returns all complete blocks
    for i in range(len(x)//n_stims):
        start = n_stims*i
        end = n_stims*(i+1)
        yield x[start:end]
    
def generate_trial_files(subject_number=1,n_blocks=7,n_stims=100):
# generates n_block trial files per subject
# each block contains n_stim trials, randomized from folder which name is inferred from subject_number
# returns an array of n_block file names
    seed = time.getTime()
    random.seed(seed)
    
    stim_folder = "sounds/Subj"+str(subject_number)
    sound_files = [os.path.basename(x) for x in glob.glob(stim_folder+"/*.wav")]

    print(len(sound_files))

    first_half = sound_files[:int(len(sound_files)/2)]
    second_half = sound_files[int(len(sound_files)/2):]
    # trials consist of two random files, one from the first half, and one from the second half of the stimulus list
    # write trials by blocks of n_stims
    block_count = 0
    trial_files = []
    for block_stims in enblock(list(zip(first_half, second_half)),n_stims):
        trial_file = 'trials/trials_subj' + str(subject_number) + '_' + str(block_count) + '_' + date.strftime('%y%m%d_%H.%M')+'.csv'
        print("generate trial file "+trial_file)
        trial_files.append(trial_file)
        with open(trial_file, 'w+', newline='') as file :
            # each trial is stored as a row in a csv file, with format: 
            # StimA,MeanA,PA1,PA2,PA3,PA4,PA5,PA6,PA7,StimB,MeanB,PB1,PB2,PB3,PB4,PB5,PB6,PB7
            # where Mean and P1...P7 are CLEESE parameters found in .txt files stored alongside de .wav stims
            # write header
            writer = csv.writer(file)
            writer.writerow(["StimA","StimB"])
            # write each trial in block
            for trial_stims in block_stims:   
                writer.writerow(trial_stims)
        # break when enough blocks
        block_count += 1
        if block_count >= n_blocks:
            break

    return trial_files

def generate_practice_trial_file(subject_number=1, n_practice_trials = 3):
# generates one file of practice trials
# the block contains a fixed nb of trials, selected randomly from the real trials
# returns one file_name
    
    seed = time.getTime()
    random.seed(seed)
    stim_folder = "sounds/Subj"+str(subject_number)
    sound_files = [os.path.basename(x) for x in glob.glob(stim_folder+"/*.wav")]
    random.shuffle(sound_files)
    first_half = sound_files[:int(len(sound_files)/2)]
    second_half = sound_files[int(len(sound_files)/2):]
    
    # each trial is stored as a row in a csv file, with format: StimA,StimB
    trial_file = 'trials/trials_subj' + str(subject_number) + '_PRACTICE_' + date.strftime('%y%m%d_%H.%M')+'.csv'
    with open(trial_file, 'w+', newline='') as file :
        # write header
        writer = csv.writer(file)
        writer.writerow(["StimA","StimB"])
        # write n_practice_trials
        for trial_stims in list(zip(first_half, second_half))[:n_practice_trials]:   
            writer.writerow(trial_stims)
    return trial_file

def read_trials(trial_file): 
# read all trials in a block of trial, stored as a CSV trial file
    with open(trial_file, 'r') as fid :
        reader = csv.reader(fid)
        trials = list(reader)
    return trials[1::] #trim header

def generate_result_file(subject_number):

    result_file = 'results/results_subj'+str(subject_number)+'_'+date.strftime('%y%m%d_%H.%M')+'.csv'        
    result_headers = ['subj','session','trial','block','sex','age','date','stim','stim_order', 'filter','filter_freq','filter_gain','response','rt']
    with open(result_file, 'w+') as file:
        writer = csv.writer(file)
        writer.writerow(result_headers)
    return result_file

def show_text_and_wait(file_name = None, message = None):
    event.clearEvents()
    if message is None:
        #with codecs.open (file_name, "r", "utf-8") as file :
        with open (file_name, "r") as file :
            message = file.read()
    text_object = visual.TextStim(win, text = message, color = 'black')
    text_object.height = 0.1
    text_object.draw()
    win.flip()
    while True :
        if len(event.getKeys()) > 0: 
            core.wait(0.2)
            break
        event.clearEvents()
        core.wait(0.2)
        text_object.draw()
        win.flip()

def show_text(file_name = None, message = None):
    if message is None:
        #with codecs.open (file_name, "r", "utf-8") as file :
        with open (file_name, "r") as file :
            message = file.read()
    text_object = visual.TextStim(win, text = message, color = 'black')
    text_object.height = 0.1
    text_object.draw()
    win.flip()

def update_trial_gui(): 
    play_instruction.draw()
    play_icon.draw()
    response_instruction.draw()
    play_icon.draw()
    for response_label in response_labels: response_label.draw()
    for response_checkbox in response_checkboxes: response_checkbox.draw()
    win.flip()

def get_false_feedback(min,max):
# returns a random percentage (int) between min and max percent
# min, max: integers between 0 and 100
    return int(100*random.uniform(float(min)/100, float(max)/100))

def play_sound(sound):
        #play sound
        audio = pyaudio.PyAudio()
#        sr,wave = wav.read(fileName)
        wf = wave.open(sound)
        def play_audio_callback(in_data, frame_count, time_info,status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)
        #define data stream for playing audio and start it
        output_stream = audio.open(format   = audio.get_format_from_width(wf.getsampwidth())
                             , channels     = wf.getnchannels()
                             , rate         = wf.getframerate()
                             , output       = True
                             , stream_callback = play_audio_callback
                        )
        output_stream.start_stream()
        while output_stream.is_active():
            core.wait(0.01)
            continue 


###########################################################################################
###      DEFINE HOW MANY TRIALS IN HOW MANY BLOCKS 
###      NOTE: if repeat_for_internal_noise, the last block is automatically repeated, 
### 	 i.e. the total nb of blocks is n_block + 1
###########################################################################################

n_blocks = 5
n_stims = 50
repeat_for_internal_noise = 1
n_practice_trials = 3

###########################################################################################

img_path = 'images/'
sound_path = 'sounds/'

# get participant nr, age, sex 
subject_info = {u'Number':1, u'Age':20, u'Sex': u'f/m', 'Session':1}
dlg = gui.DlgFromDict(subject_info, title=u'REVCOR')
if dlg.OK:
    subject_number = subject_info[u'Number']
    subject_age = subject_info[u'Age']
    subject_sex = subject_info[u'Sex']
    subject_session = subject_info[u'Session']    
else:
    core.quit() #the user hit cancel so exit
date = datetime.datetime.now()
time = core.Clock()

# create stimuli if folder don't exist
# warning: if folder exists with wrong number of stims
output_folder = sound_path + 'Subj' + str(subject_number)
if not os.path.exists(output_folder):
    assert("Can't find stimulus folder: "+output_folder)
	# generate_stimuli(subject_number, n_blocks=n_blocks, n_stims=n_stims, base_sound='./sounds/male_vraiment_flat.wav', config_file='./config.py')

win = visual.Window([1366,768],fullscr=False,color="lightgray", units='norm')
screen_ratio = (float(win.size[1])/float(win.size[0]))
isi = .5

# trial gui
question = 'Quelle prononciation est la plus souriante ?'
response_options = ['[g] voix 1','[h] voix 2']
response_keys = ['g', 'h']
label_size = 0.1
play_instruction = visual.TextStim(win, units='norm', text='[Space] Voix 1 & 2', color='red', height=label_size, pos=(0,0.5))
response_instruction = visual.TextStim(win, units='norm', text=question, color='black', height=label_size, pos=(0,0.1), alignHoriz='center')
play_icon = visual.ImageStim(win, image=img_path+'play_off.png', units='norm', size = (0.15*screen_ratio,0.15), pos=(0,0.5+2*label_size))
response_labels = []
response_checkboxes = []
reponse_ypos = -0.2
reponse_xpos = -0.1
label_spacing = abs(-0.8 - reponse_ypos)/(len(response_options)+1)
for index, response_option in enumerate(response_options):
    y = reponse_ypos - label_spacing * index
    response_labels.append(visual.TextStim(win, units = 'norm', text=response_option, alignHoriz='left', height=label_size, color='black', pos=(reponse_xpos,y)))
    response_checkboxes.append(visual.ImageStim(win, image=img_path+'rb_off.png', size=(label_size*screen_ratio,label_size), units='norm', pos=(reponse_xpos-label_size, y-label_size*.05)))

# generate data files
result_file = generate_result_file(subject_number)
trial_files = generate_trial_files(subject_number,n_blocks,n_stims)
# add practice block in first positio
practice_file = generate_practice_trial_file(subject_number, n_practice_trials)
trial_files.insert(0, practice_file)
# duplicate last block (for internal noise computation)
if repeat_for_internal_noise:
	trial_files.append(trial_files[-1])

# experiment 
show_text_and_wait(file_name="intro.txt")  
show_text_and_wait(file_name="practice.txt")  
trial_count = 0
n_blocks = len(trial_files)
for block_count, trial_file in enumerate(trial_files):
    block_trials = read_trials(trial_file)
    for trial in block_trials :
        # focus play instruction and reset checkboxes
        play_instruction.setColor('red')
        play_icon.setImage(img_path+'play_on.png')
        for checkbox in response_checkboxes:
            checkbox.setImage(img_path+'rb_off.png')
        sound_1 = sound_path+'Subj'+str(subject_number)+'/'+trial[0]
        sound_2 = sound_path+'Subj'+str(subject_number)+'/'+trial[1]
        end_trial = False
        while (not end_trial):
            update_trial_gui()
            # upon play command...
            if event.waitKeys()==['space']: 
                # unfocus play instruction
                play_instruction.setColor('black')
                play_icon.setImage(img_path+'play_off.png')
                update_trial_gui()
                # play sounds
                play_sound(sound_1)
                core.wait(isi)
                play_sound(sound_2)
                # focus response instruction
                response_start = time.getTime()
                response_instruction.setColor('red')
                update_trial_gui()
                # upon key response...
                response_key = event.waitKeys(keyList=response_keys)
                response_time = time.getTime() - response_start
                # unfocus response_instruction, select checkbox
                response_instruction.setColor('black')
                response_checkboxes[response_keys.index(response_key[0])].setImage(img_path+'rb_on.png')
                update_trial_gui()
                # blank screen and end trial
                core.wait(0.3) 
                win.flip()
                core.wait(0.2) 
                end_trial = True
        
        # log response
        row = [subject_number, subject_session, trial_count, block_count, subject_sex, subject_age, date]
        if response_key == ['g']:
            response_choice = 0
        elif response_key == ['h']:
            response_choice = 1
        
        with open(result_file, 'a') as file :
            writer = csv.writer(file,lineterminator='\n')
            for stim_order,stim in enumerate(trial): 
            	filters = get_stim_info(folder=sound_path+'Subj'+str(subject_number), file_name=stim)
            	for filter_counter, filter_info in enumerate(filters):
            		result = row + [stim,stim_order,filter_counter,filter_info[0],filter_info[1],response_choice==stim_order,round(response_time,3)]
            		writer.writerow(result)

        trial_count += 1
        
    # inform end of practice at the end of first block
    if block_count == 0:
       show_text_and_wait(file_name="end_practice.txt") 
       practice_block = False 
    # pause at the end of subsequent blocks 
    elif block_count < n_blocks-1: 
        show_text_and_wait(message = "Vous avez fait "+str(Fraction(block_count, n_blocks-1))+u" de l'experience.\n Votre score sur cette partie de l'experience est de "+ str(get_false_feedback(70,85)) +u"%.\n\n (Appuyez sur une touche pour continuer).")
        show_text("pause1.txt")
        core.wait(5)
        show_text_and_wait("pause0.txt")         
        
        
#End of experiment
show_text_and_wait("end.txt")

# Close Python
win.close()
core.quit()
sys.exit()
