import csv
import midiutil
import numpy
import math
import random
from scipy import stats
from datetime import datetime


csv_input = "data/09-22.csv"
midi_output = "midi/09-22-06.mid"




def save_midi(midi_file):
  filename = midi_output
  with open(filename, 'wb') as output_file:
      midi_file.writeFile(output_file)
      print('midi file saved')

def get_note(count, stats):
  major_scale = [60, 62, 64, 65, 67, 69, 71]
  if count == 1:
    return major_scale[0]
  if count < 3:
    return major_scale[1]
  if count < 6:
    return major_scale[2]
  if count < 11:
    return major_scale[3]
  if count < 16:
    return major_scale[4]
  if count < 23:
    return major_scale[5]
  else:
    return major_scale[6]

def get_random_chord(scale):
  chord_start = random.randrange(0, len(scale), 1)
  chord = [scale[chord_start], scale[(chord_start+2)%len(scale)], scale[(chord_start+4)%len(scale)]]
  return chord

def compose_midi(data, stats):
  track = 0
  channel = 0
  time = 0 # in beats
  tempo = 600  # beats per minute
  volume = 100 # from 0-127
  program = 0 # Midi instrument
  midi_file = midiutil.MIDIFile(1, deinterleave=False, adjust_origin=False)
  midi_file.addTempo(track, time, tempo)
  midi_file.addProgramChange(track, channel, time, program)

  time_bg = 0
  midi_file.addProgramChange(track, channel+1, time_bg, 41)
  duration = 1 #in beats

  for row in data:
    # print((len(row) - stats['mean']) / stats['stdev'])
    if(len(row) == 0):
      midi_file.addNote(track, channel, 60, time, duration, 0)
    else:
      note = get_note(len(row), stats) 
      # note_idx = math.floor(numpy.interp(len(row), [stats['minimum'], stats['maximum']], [0,6]))
      midi_file.addNote(track, channel, note, time, duration, 100)
    time = time + duration

  # time = 0 # in beats
  # for row in reversed(data):
  #   # print((len(row) - stats['mean']) / stats['stdev'])
  #   if(len(row) == 0):
  #     midi_file.addNote(track, channel, 60, time, duration, 0)
  #   else:
  #     note = get_note(len(row), stats) 
  #     # note_idx = math.floor(numpy.interp(len(row), [stats['minimum'], stats['maximum']], [0,6]))
  #     midi_file.addNote(track, channel+1, note, time, duration, 100)
  #   time = time + duration


  # #background .. 
  # major_scale = [25, 27, 29, 30, 32, 34, 36]
  # chord = get_random_chord(major_scale)
  # chord_idx = 0
  # duration_bg = 2
  # for step in range(0, math.ceil(len(data)/2)):
  #   midi_file.addNote(track, channel+1, chord[chord_idx], time_bg, duration_bg, 40)
  #   time_bg = time_bg + duration_bg
  #   chord_idx += 1
  #   if chord_idx >= len(chord):
  #     chord_idx = 0
  #     chord = get_random_chord(major_scale)




  save_midi(midi_file)



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

  # for i in binned_data:
  #   print(len(i))
  # print(len(binned_data[20]))
  return binned_data


with open(csv_input, 'rt') as csvfile:
  reader = csv.DictReader(csvfile, quotechar='"')
  all_data = []
  for row in reader:
    all_data.append(row)

  binned_data = bin_data(all_data, 60.0)
  stats = get_stats(binned_data)
  compose_midi(binned_data, stats)
    
