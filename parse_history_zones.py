import csv
import midiutil
import numpy
import math
import random
from scipy import stats
from datetime import datetime


ny_input = "data/09-22.csv"
nd_input = "data/08-07.csv"
midi_output = "midi/new-tests/01.mid"


def get_note(scale, count, stats):
  if count == 1:
    return scale[0] #1
  if count < 3:
    return scale[1] #2
  if count < 6:
    return scale[2] #3
  if count < 11:
    return scale[3] #4
  if count < 16:
    return scale[4] #5
  if count < 23:
    return scale[5] #6
  else:
    return scale[6] #7

def get_random_chord(scale):
  chord_start = random.randrange(0, len(scale), 1)
  chord = [scale[chord_start], scale[(chord_start+2)%len(scale)], scale[(chord_start+4)%len(scale)]]
  return chord

def get_duration(transition):
  # 0 most most common, default
  # 1 5 7 8 most common
  durations = [1, 1.25, 1.5, 2]
  if transition == 0:
    return durations[random.randrange(0, len(durations), 1)]
  if transition >= 7 : # 7 or 8
    return durations[1] 
  if transition == 1 or transition == 5:
    return durations[2]
  else:
    return durations[3]

def init_midi(track, time, tempo):
  midi_file = midiutil.MIDIFile(1, deinterleave=False, adjust_origin=False)
  midi_file.addTempo(track, time, tempo)
  return midi_file


def compose_midi(midi_file, track, time, channel, program, scale, data, stats):
  midi_file.addProgramChange(track, channel, time, program)
  midi_file.addProgramChange(track, channel+1, time, 33)
  duration = 1
  for idx, row in enumerate(data):
    if(len(row) == 0):
      midi_file.addNote(track, channel, 60, time, duration, 0)
    else:
      note = get_note(scale, len(row), stats) 
      i = random.randrange(0, len(row), 1)
      x = int(row[i]["transition"])
      y = get_duration(x & 0xff)
      midi_file.addNote(track, channel, note, time, duration, 100)

    time = time + duration


def add_bg_track(midi_file, data_size, channel, program):
  midi_file.addProgramChange(0, channel, 0, program)
  duration = 1
  time = 0
  for i in range(data_size):
    if i%8 == 0:
      midi_file.addNote(0, channel, 36, time, duration*2, 80)
    # if (i+1)%8 == 0:
    #   midi_file.addNote(0, channel, 44, time, duration*2, 20)
    time = time + duration

  # return midi_file

def save_midi(midi_file):
  filename = midi_output
  print(filename)
  with open(filename, 'wb') as output_file:
      midi_file.writeFile(output_file)
      print('midi file saved')

def get_stats(binned_data):
  vals = list(map(lambda x: len(x), binned_data))
  minimum = numpy.amin(vals)
  maximum = numpy.amax(vals)
  stdev = numpy.std(vals)
  mean = numpy.mean(vals)
  median = numpy.median(vals)
  mode = stats.mode(vals)
  return {
    "minimum": minimum,
    "maximum": maximum,
    "mean": mean, 
    "median": median, 
    "mode": mode[0],
    "stdev": stdev
  }

#bin size is in seconds
def bin_data(data, bin_size):
  binned_data = []
  bin_count = math.floor(24*60*60 / bin_size) #total seconds in a day / bin_size
  for x in range(0, bin_count):
    binned_data.append([])

  for row in data:
    d = datetime.strptime(row['visit_local_time'], "%Y-%m-%d %H:%M:%S")
    seconds_from_day_start = d.second + d.minute*60 + d.hour*60*60
    binned_data[math.floor(seconds_from_day_start/bin_size)].append(row)

  return binned_data


def convert_to_midi(filename, midi_file, bin_size, channel, program, scale):
  with open(filename, 'rt') as csvfile:
    reader = csv.DictReader(csvfile, quotechar='"')
    all_data = []
    transitions = [0,0,0,0,0,0,0,0,0,0,0,0]
    for row in reader:
      x = int(row["transition"])
      y = x & 0xff
      transitions[y] += 1
      all_data.append(row)

    print(transitions)
    binned_data = bin_data(all_data, bin_size)
    stats = get_stats(binned_data)
    
    compose_midi(midi_file, 0, 0, channel, program, scale, binned_data, stats)


tempo = 600
bin_size = 60 

# bps = 10
# bin_count = (24*60*60/bin_size) 
# bpm = bps * 60

midi_file = init_midi(0, 0, tempo)


# guitar, c2 - c4
convert_to_midi(ny_input, midi_file, bin_size, 0, 24, [36, 40, 43, 47, 50, 53, 57])
# viola, c3 - c5
convert_to_midi(nd_input, midi_file, bin_size, 1, 41, [48, 52, 55, 59, 62, 65, 69])

add_bg_track(midi_file, int(24*60*60/bin_size), 9, 0)
save_midi(midi_file)



    
