#!/usr/bin/env python
# coding: utf-8

# # Jamendo: Querying MongoDB 

# ### Helper variables and functions

# In[1]:


import requests
import json
import urllib
import pprint

import itertools
chord_types = ['maj', 'min', '7', 'maj7', 'min7']
chromas = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
all_chords = [''.join(x) for x in itertools.product(chromas, chord_types)]


# In[2]:


import IPython.display
def jamendo_link(jamendo_id):
    return 'http://jamen.do/t/{}'.format(jamendo_id)
def jamendo_player(jamendo_id):
    IPython.display.display(IPython.display.IFrame('//widgets.jamendo.com/v3/track/{}?width=500'.format(jamendo_id), width=500, height=170))


# ### Connect to DB
# 
# https://docs.atlas.mongodb.com/driver-connection/

# In[3]:


import pymongo
client = pymongo.MongoClient('mongodb://rshukla:NtUPKACK4DjMaT4X@c4dm-xenserv-virt5.eecs.qmul.ac.uk')
# client = pymongo.MongoClient('localhost', 2701)
db = client.audiocommons
collection = db.descriptors


# ### Style Arrays

# In[ ]:


allstyles=[]

# Store the style list variables in a global list
styles = ['metal','rock','rnb','hiphop','jazz','blues','indie','punk','filmscore',
          'classical','dance','house','chillout','ambient','electronic','folk','country',
          'latin','reggae']

# Create 
style_labels = {}


for n in range(len(styles)):
    style_labels[n]=str(styles[n])
    print(style_labels[n])
    styles[n]=[]


# ### Query tracks

# In[ ]:


from csv import writer
from csv import reader

header_fields = []
print(header_fields)

# Loop through and query each listed style
# Remove the query header and store the result as JSON
for x in range(19):
    address = ("https://api.jamendo.com/v3.0/tracks/?client_id=214f0f1a&format=json&limit=all&boost=listens_total&fuzzytags="+style_labels[x]+"&lang=en&include=musicinfo")
    response = requests.get(address)
    data = response.json()
    data.pop("headers")
    
    # open the file in the write mode
    with open(style_labels[x]+".csv", 'w') as genre:
        # create the csv writer
        line_writer = writer(genre)

        # Create the header fields
        # For each field find and write the dict key to a list
        if x == 0:
            for column in data['results'][x]:
                # In the case of the musicinfo field, write the sub-fields
                if column=="musicinfo":
                    for subcolumn in data['results'][x]['musicinfo']:
                        if subcolumn !="tags":
                            header_fields.append(subcolumn)
                        else:
                            for subsubcolumn in data['results'][x]['musicinfo']['tags']:
                                header_fields.append(subsubcolumn)    
                # Otherwise, just write the main field
                else:                    
                    header_fields.append(column)
            # Write two identifier fields
            header_fields.append('Rank')
            header_fields.append('Genre')
        # Assign the field names to the column header    
        line_writer.writerow(header_fields)

        # Write every record from the style to the dataframe 
        for y in range(len(data['results'])):
            # Create and empty list to store each record serially
            track_data = []
            # For each field find and write the value to the list
            for column in data['results'][y]:
                # In the case of the musicinfo field, write the sub-fields
                if column=="musicinfo":
                    for subcolumn in data['results'][y]['musicinfo']:
                        if subcolumn !="tags":
                            track_data.append(data['results'][y]['musicinfo'][subcolumn])
                        else:
                            for subsubcolumn in data['results'][y]['musicinfo']['tags']:
                                track_data.append(data['results'][y]['musicinfo']['tags'][subsubcolumn])
                # Otherwise, just write the main field
                else:
                    track_data.append(data['results'][y][column])
                if column=="id":
                    styles[x].append("jamendo-tracks:"+str(data['results'][y]['id']))
             # Write two identifier fields
            track_data.append(y)
            track_data.append(style_labels[x])
            # Assign the field names to the column header                                
            line_writer.writerow(track_data)
        print(styles[x])
        genre.close()


# In[ ]:





# ### Create track lists

# In[ ]:


print(track_data)
print(header_fields)


# ### Query by musical parameters

# In[11]:


collection.count_documents({
    #Count tracks with the required major or minor keys ...
    "$and":[
        {"$or":[
            #List required major key conditions
            {"$and":[
                {"$or":[
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'A#'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'C'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'D'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'E'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'F#'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'G#'}}
                ]},
                {'essentia-music.tonal.key_krumhansl.scale':{"$eq": 'major'}}            
            ]},
            #List required minor key conditions
            {"$and":[
                {"$or":[
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'G'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'A'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'B'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'C#'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'D#'}},
                    {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'F'}}
                ]},
                {'essentia-music.tonal.key_krumhansl.scale':{"$eq": 'minor'}}  

            ]}
        ]},
        #... rhythmic range
        {"$and":[
            {'essentia-music.rhythm.bpm':{"$gte": 118}},
            {'essentia-music.rhythm.bpm':{"$lte": 143}}
        ]},
        #... and dissonance range
        {"$and":[
            {'essentia-music.lowlevel.dissonance.mean':{"$gte": 0.46}},
            {'essentia-music.lowlevel.dissonance.mean':{"$lte": 0.5}}
        ]}
    ]}
)


# ### Return specified tracks with musical parameter values

# In[ ]:


from csv import writer
from csv import reader

header = []
print(header)
header = header_fields
print(header)
header.append('ID_Verify')
header.append('Dissonance')
header.append('BPM')
header.append('Key')
header.append('Scale')
header.append('Danceability')
header.append('Pulse')

track_ids=[]

# Create a new .csv file to append selections
with open('selections.csv','w', newline='\n') as selections:
    # Create .csv writer instance
    line_writer=writer(selections)
    line_writer.writerow(header)
    
    # Open each .csv file
    for n in range(len(styles)):
        # Search the Jamendo database
        for piece in collection.find(
            {
            "$and":[
                # Make sure the track ID is contained in the style list
                {'_id':{"$in": styles[n]}},
                # Make sure the track key qualifies
                {"$or":[
                    # Either as one of the permitted major key conditions ...
                    {"$and":[
                        {"$or":[
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'A#'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'C'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'D'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'E'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'F#'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'G#'}}
                        ]},
                        {'essentia-music.tonal.key_krumhansl.scale':{"$eq": 'major'}}            
                    ]},
                    # ... or as one of the permitted major key conditions.
                    {"$and":[
                        {"$or":[
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'G'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'A'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'B'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'C#'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'D#'}},
                            {'essentia-music.tonal.key_krumhansl.key':{"$eq": 'F'}}
                        ]},
                        {'essentia-music.tonal.key_krumhansl.scale':{"$eq": 'minor'}}  

                    ]}
                ]},
                # Make sure the track tempo qualifies
                {"$or":[
                    {"$and":[
                        {'essentia-music.rhythm.bpm':{"$gte": 77}},
                        {'essentia-music.rhythm.bpm':{"$lte": 87}}
                    ]},
                    {"$and":[
                        {'essentia-music.rhythm.bpm':{"$gte": 95}},
                        {'essentia-music.rhythm.bpm':{"$lte": 110}}
                    ]},
                    {"$and":[
                        {'essentia-music.rhythm.bpm':{"$gte": 118}},
                        {'essentia-music.rhythm.bpm':{"$lte": 143}}
                    ]}                            
                ]},
                #... and dissonance range
                {"$or":[
                    {"$and":[
                        {'essentia-music.lowlevel.dissonance.mean':{"$gte": 0.0}},
                        {'essentia-music.lowlevel.dissonance.mean':{"$lte": 0.42}}
                    ]},
                    {"$and":[
                        {'essentia-music.lowlevel.dissonance.mean':{"$gte": 0.44}},
                        {'essentia-music.lowlevel.dissonance.mean':{"$lte": 0.46}}
                    ]},
                    {"$and":[
                        {'essentia-music.lowlevel.dissonance.mean':{"$gte": 0.47}},
                        {'essentia-music.lowlevel.dissonance.mean':{"$lte": 0.5}}
                    ]}                           
                ]}
            ]},

            # Return the record with required fields
            {'essentia-music.lowlevel.dissonance.mean': True,
             'essentia-music.rhythm.bpm': True,
             'essentia-music.tonal.key_krumhansl.scale': True,
             'essentia-music.tonal.key_krumhansl.key': True,
             'essentia-music.rhythm.danceability': True,
             'essentia-music.rhythm.beats_loudness.mean': True
            }

        ):

            # Parse the data using string search and strip
            # Use unique strings to define markers
            markers = [int(str(piece).index("tracks")),
                       int(str(piece).index("essentia")),
                       int(str(piece).index("dissonance")),
                       int(str(piece).index("rhythm")),
                       int(str(piece).index("bpm")),
                       int(str(piece).index("danceability")),
                       int(str(piece).index("krumhansl")),
                       int(str(piece).index("scale")),
                       int(str(piece).index("beats"))
                      ]
            # Use marker references to strip required data into fields
            track = str(piece)[markers[0]+7:markers[1]-4]
            dissonance = str(piece)[markers[2]+22:markers[3]-5]
            tempo = str(piece)[markers[4]+6:markers[5]-3]
            key = str(piece)[markers[6]+21:markers[7]-4]
            scale = str(piece)[markers[7]+9:markers[7]+14]
            groove = str(piece)[markers[5]+15:markers[6]-18]
            pulse = str(piece)[markers[8]+26:markers[4]-4]
            print(track,dissonance,tempo,key,scale,groove,pulse)

            with open(style_labels[n]+".csv",'r') as songs:
                # Create .csv reader instance
                line_reader=reader(songs)
                # Read each line of the .csv
                for line in line_reader:
                    # Find the record in the source files
                    if track in line:
                        track_ids.append(track)
                        # Append the additional field data
                        line.append(f'{track}')
                        line.append(f'{dissonance}')
                        line.append(f'{tempo}')
                        line.append(f'{key}')
                        line.append(f'{scale}')
                        line.append(f'{groove}')
                        line.append(f'{pulse}')
                        # Write the file to a new line
                        line_writer.writerow(line)
                songs.close()
    selections.close()


# ### Dowload selected tracks

# In[ ]:


import pandas
shortlist = pandas.read_csv('selections.csv')
print(len(shortlist))

for z in range(len(shortlist)):
    # check download URL
    print(shortlist.audiodownload[z])
    # check track name
    print(shortlist.name[z])
    # load audio file from URL
    audio = requests.get(shortlist.audiodownload[z])
    # comp filename with underscore inserted for blankspace 
    filename=shortlist.name[z][:20].replace(" ","_").replace(".","").replace("(","").replace(")","").replace("'","") + ".mp3"
    # write the audio file to disk
    with open("./tracks/" + filename,'wb') as mp3_file:
        mp3_file.write(audio.content)
    # confirm download and progress
    print("Download completed!")
    print(z)


# ### Create voiceover announcements for each track

# In[ ]:


from os import system
for example in range(len(shortlist)):
    # compile the artist name, without punctuation
    artist = shortlist.artist_name[example].replace(" ","_").replace(".","").replace("(","").replace(")","").replace("'","").replace(":","").replace("&amp;","and").replace("&quot;","").replace("&"," and ").replace("&#039;","")
    # compile the track name, without punctuation
    title = shortlist.name[example].replace(" ","_").replace(".","").replace("(","").replace(")","").replace("'","").replace(":","").replace("&amp;","and").replace("&quot;","").replace("&","and").replace("&#039;","")
    # compile the voiceover announcement
    announcement = artist + ' – ' + title
    # comp filename with underscore inserted for blankspace 
    filename=shortlist.name[example][:20].replace(" ","_").replace(".","").replace("(","").replace(")","").replace("'","") + "_VXO"
    # save the voiceover announcement with track name
    settings = 'say -v Serena -r 135 -o ' "./announcements/" + filename + '.wav --file-format=WAVE --data-format=I16@44100 ' + announcement
    print(settings)
    system(settings)


# ### Create new playlist file based on folder content

# In[3]:


import os
from csv import writer

# Create a new .csv file to append selections
with open('./testing/Task3.csv','w', newline='\n') as choices:
    # Create .csv writer instance
    choiceInfo=writer(choices)
    for file in os.scandir('./testing/Task3'):
        if file.path.endswith(".mp3") and file.is_file():
            choiceInfo.writerow([file.name])
choices.close()

