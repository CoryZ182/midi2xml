# midi2xml
midi2xml contains functions to read xml files as midi data, and write midi data to xml files

magenta is required for the read_from_xml function. It can be found here: https://magenta.tensorflow.org/

pretty_midi is a library containing functions/classes for the manipulation of midi data. It is required for this library to work.
It can be found here: https://github.com/craffel/pretty-midi

### example reading an xml file into midi data

import midi_xml_read_write as xml_rw
import pretty_midi
#ead xml file
midi_data = xml_rw.read_from_xml('example.mxl')
#midi_data is a PrettyMIDI object compatible with pretty_midi

### example reading a midi file, and writing it to an xml file

import midi_xml_read_write as xml_rw
import pretty_midi
#create PrettyMIDI object from midi file
midi_data = pretty_midi.PrettyMIDI('example.mid')
write midi_data to xml file
xml_rw.write_to_xml(midi_data, 'example.mxl')