from magenta.music import musicxml_reader
import magenta.music
import pretty_midi
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree

"""given the current measure, number of accidentals in the key (- for flats, + for sharps), and the current time signature,
returns an element containing attributes for the current measure"""
def write_measure_attributes(current_measure, key_accidentals, time_signature, clef_type):
    attributes = ET.Element('attributes')
    #smallest note size possible, in fractions of quarter notes. 8 allows notes as small as 32nd notes
    divisions = ET.SubElement(attributes, 'divisions')
    divisions.text = '24'
    key = ET.SubElement(attributes, 'key')
    fifths = ET.SubElement(key, 'fifths')
    fifths.text = str(key_accidentals)
    time = ET.SubElement(attributes, 'time')
    beats = ET.SubElement(time, 'beats')
    beats.text = str(time_signature.numerator)
    beatType = ET.SubElement(time, 'beat-type')
    beatType.text = str(time_signature.denominator)
    #treble is G2, bass is F4 (else assumes treble)
    clef = ET.SubElement(attributes, 'clef')
    sign = ET.SubElement(clef, 'sign')
    if clef_type == 'bass':
        sign.text = 'F'
    else:
        sign.text = 'G'
    line = ET.SubElement(clef, 'line')
    if clef_type == 'bass':
        line.text = '4'
    else:
        line.text = '2'
    return attributes

"""returns note type (whole note, half note, etc.)"""
def get_note_type(note_duration):
    note_type = ''
    while note_duration >= 4:
        if note_type != '':
            note_type += '+'
        #length 192
        if note_duration >= 190:
            note_duration -= 192
            note_type += 'breve'
        #length 168
        elif note_duration >= 166:
            note_duration -= 168
            note_type += 'ddwhole'
        #length 144
        elif note_duration >= 142:
            note_duration -= 144
            note_type += 'dwhole'
        #length 96
        elif note_duration >= 94:
            note_duration -= 96
            note_type += 'whole'
        #length 84
        elif note_duration >= 82:
            note_duration -= 84
            note_type += 'ddhalf'
        #length 72
        elif note_duration >= 70:
            note_duration -= 72
            note_type += 'dhalf'
        #length 48
        elif note_duration >= 46:
            note_duration -= 48
            note_type += 'half'
        #length 42
        elif note_duration >= 40:
            note_duration -= 42
            note_type += 'ddquarter'
        #length 36
        elif note_duration >= 34:
            note_duration -= 36
            note_type += 'dquarter'
        #length 24
        elif note_duration > 22:
            note_duration -= 24
            note_type += 'quarter'
        #length 21
        elif note_duration >= 20:
            note_duration -= 21
            note_type += 'ddeighth'
        #length 18
        elif note_duration >= 16:
            note_duration -= 18
            note_type += 'deighth'
        #length 12
        elif note_duration >= 10:
            note_duration -= 12
            note_type += 'eighth'
        #length 9
        elif note_duration >= 8:
            note_duration -= 9
            note_type += 'd16th'
        #length 6
        elif note_duration >= 4:
            note_duration -= 6
            note_type += '16th'
        else:
            break
    if note_type == '' and note_duration > 0:
        return '32nd'
    if note_type[-1] == '+':
        return note_type[:-1]
    return note_type

"""
creates a note Element
note_name
    string containing name of note's pitch (C4, D#6, A2, etc.)
note_duration
    integer containing the nuber of divisions the note lasts
note_type
    string containing note type(s) needed to create a note ('half+eighth', 'ddquarter', '16th', etc.)
note_start
    False if this note is tied to a previous note (this isn't the start of the note)
note_end
    False if this note ties over to another note (this isn't the end of the note)
note_voice
    integer representing voice of part (for instruments that play multiple notes at once)

returns: note Element
"""
def create_note(note_name, note_duration, note_type, note_start = True, note_end = True, note_voice = 1):
    #if impossible to create note of correct duration with 1 note, creates multiple and ties them together
    #example: duration of half note + eighth note cannot be made using a single valid note duration
    compoundNote = True
    notes = list()
    splitPoint = 0
    while compoundNote:
        prevSplit = splitPoint
        splitPoint = str(note_type).find('+', (prevSplit+1))
        if splitPoint == -1:
            compoundNote = False
        #create note
        currentNote = ET.Element('note')
        pitch = ET.SubElement(currentNote, 'pitch')
        step = ET.SubElement(pitch, 'step')
        step.text = str(note_name[0])
        #checks for accidentals (only natural/sharp/flat)
        if len(note_name) == 3:
            #natural
            if note_name[1] != chr(9838):
                alter = ET.SubElement(pitch, 'alter')
                #sharp
                if note_name[1] == chr(9839) or note_name[1] == '#':
                    alter.text = '1'
                #flat
                else:
                    alter.text = '-1'
        octave = ET.SubElement(pitch, 'octave')
        octave.text = str(note_name[-1])
        #determines length of current note, in case of multiple notes
        if splitPoint == -1:
            if prevSplit == 0:
                currentNoteType = str(note_type)
            else:
                #note_type[prevSplit+1:] doesn't read properly (resulting in type "[]")
                currentNoteType = str(note_type[(prevSplit+1):])
        else:
            if prevSplit == 0:
                currentNoteType = str(note_type[:splitPoint])
            else:
                currentNoteType = str(note_type[(prevSplit+1):splitPoint])

        #duration of current note
        if compoundNote:
            noteDuration = 1
            if currentNoteType.find('breve') != -1:
                noteDuration = 192
            elif currentNoteType.find('whole') != -1:
                noteDuration = 96
            elif currentNoteType.find('half') != -1:
                noteDuration = 48
            elif currentNoteType.find('quarter') != -1:
                noteDuration = 24
            elif currentNoteType.find('eighth') != -1:
                noteDuration = 12
            elif currentNoteType.find('16th') != -1:
                noteDuration = 6
            elif currentNoteType.find('32nd') != -1:
                noteDuration = 3

            if currentNoteType.find('dd') != -1:
                noteDuration *= 1.75
            elif currentNoteType.find('d') != -1:
                noteDuration *= 1.5
            noteDuration = round(noteDuration)
            note_duration -= noteDuration
        else:
            noteDuration = note_duration
        duration = ET.SubElement(currentNote, 'duration')
        duration.text = str(noteDuration)

        #ties
        if not note_start or prevSplit != 0:
            ET.SubElement(currentNote, 'tie', type="stop")
        if not note_end or splitPoint != -1:
            ET.SubElement(currentNote, 'tie', type="start")
        voice = ET.SubElement(currentNote, 'voice')
        voice.text = str(note_voice)
        note_type = ET.SubElement(currentNote, 'type')
        if currentNoteType[0:2] == 'dd':
            note_type.text = currentNoteType[2:]
            ET.SubElement(currentNote, 'dot')
            ET.SubElement(currentNote, 'dot')
        elif currentNoteType[0] == 'd':
            note_type.text = currentNoteType[1:]
            ET.SubElement(currentNote, 'dot')
        else:
            note_type.text = currentNoteType
        notes.append(currentNote)
    return notes

def read_from_xml(xml_file):
    """Reads an xml file into a prettyMIDI object.

    Args:
    xml_file : str
        path to a musicxml file

    Returns:
        a prettyMIDI object
    """
    xml_note_sequence = musicxml_reader.musicxml_file_to_sequence_proto(xml_file)
    return magenta.music.sequence_proto_to_pretty_midi(xml_note_sequence)

def write_to_xml(self, midi_object, filename):
    """writes a prettyMIDI object to a musicxml file.

    Args:
    midi_object : PrettyMIDI
        midi data to be written
    filename : str
        path to write xml file to
    """
    song = midi_object
    root = ET.Element('score-partwise')
    tree = ET.ElementTree(root)
    partList = ET.SubElement(root, 'part-list')
    #removes notes with a duration less than 0 (note.end is at the same time or before note.start)
    song.remove_invalid_notes()
    #numbers parts 'P1', 'P2', etc. 
    instNum = 1
    for instrument in song.instruments:
        if instrument.is_drum == False:
            instId = 'P' + str(instNum)
            partID = ET.SubElement(partList, 'score-part', id=instId)
            partName = ET.SubElement(partID, 'part-name')
            partName.text = instrument.name
            instNum += 1
    #list containing the time stamp of each downbeat (1st beat in each measure)
    downbeats = song.get_downbeats()
    #list containing time signature of piece, as well as time stamp when time signature changes
    timeSignatures = song.time_signature_changes
    #list containing key signature of piece, as well as time stamp when key signature changes
    keySignatures = song.key_signature_changes

    #same as before, resets before the for loop
    instNum = 1
    for instrument in song.instruments:
        if instrument.is_drum == False:
            #labels id in part element, matches id from above
            instId = 'P' + str(instNum)
            # i keeps track of measures, based on prettymidi's downbeats list
            i = 0
            # j keeps track of time signature, based on prettymidi's time signature changes list
            j = 0
            # k keeps track of key signature, based on prettymidi's key signature changes list
            k = 0
            #create part
            part = ET.SubElement(root, 'part', id=instId)
            #measure by measure loop
            while i  < len(downbeats):
                currentMeasure = i+1
                #finds current time signature
                while j+1 < len(timeSignatures) and downbeats[i] >= timeSignatures[j+1].time:
                    j += 1
                currentTime = timeSignatures[j]
                #finds current key signature
                while k+1 < len(keySignatures) and downbeats[i] >= keySignatures[k+1].time:
                    k += 1
                currentKey = pretty_midi.key_number_to_mode_accidentals(keySignatures[k].key_number)
                #finds length of measure in seconds
                if currentMeasure == len(downbeats):
                    measureLength = song.get_end_time()-downbeats[i]
                else:
                    measureLength = downbeats[i+1]-downbeats[i]
                #divisions per measure. Calculates the total number of divisions in the current measure (24 divisions per quarter note)
                dpm = (timeSignatures[j].numerator/timeSignatures[j].denominator)*4*24
                #keeps track of divisions, which is used to know current position in the measure
                numDivisions = 0
                #true if there is a note present in this measure
                isNote = False
                #determines if treble or bass clef (only these 2 for simplicity; no changes throughout piece)
                treble = 0
                bass = 0
                for note in instrument.notes:
                    noteName = pretty_midi.note_number_to_name(note.pitch)
                    if int(noteName[-1]) >= 4:
                        treble += 1
                    else:
                        bass += 1
                if treble >= bass:
                    clef_type = 'treble'
                else:
                    clef_type = 'bass'
                voiceNum = 1
                
                #create measure
                measure = ET.SubElement(part, 'measure', number=str(currentMeasure))
                measure.append(write_measure_attributes(currentMeasure, currentKey[1], currentTime, clef_type))
                #if note is in measure, adds note element
                for note in instrument.notes:
                    #if note starts in current measure
                    #(note starts on or after downbeat of this measure) and ((this is the last measure) or (note starts before downbeat of next measure))
                    if round(((note.start-downbeats[i])/measureLength)*dpm) >= 0 and ((currentMeasure == len(downbeats) or round(((note.start-downbeats[i+1])/measureLength)*dpm) < 0)):
                        isNote = True
                        if numDivisions < round(((note.start-downbeats[i])/measureLength)*dpm):
                            forward = ET.SubElement(measure, 'forward')
                            duration = ET.SubElement(forward, 'duration')
                            duration.text = str(round(((note.start-downbeats[i])/measureLength)*dpm)-numDivisions)
                            numDivisions = round(((note.start-downbeats[i])/measureLength)*dpm)
                            voiceNum = 1
                        elif numDivisions > round(((note.start-downbeats[i])/measureLength)*dpm):
                            backup = ET.SubElement(measure, 'backup')
                            duration = ET.SubElement(backup, 'duration')
                            duration.text = str(numDivisions-round(((note.start-downbeats[i])/measureLength)*dpm))
                            numDivisions = round(((note.start-downbeats[i])/measureLength)*dpm)
                            voiceNum += 1

                        noteName = pretty_midi.note_number_to_name(note.pitch)
                        #if note ends in current measure
                        #(this is last measure) or (note ends before or on downbeat of next measure)
                        if currentMeasure == len(downbeats) or round(((note.end-downbeats[i+1])/measureLength)*dpm) <= 0:
                            durationNum = round(((note.end-note.start)/measureLength)*dpm)
                            noteType = get_note_type(durationNum)
                            notes = create_note(noteName, durationNum, noteType, True, True, voiceNum)
                            for currentNote in notes:
                                measure.append(currentNote)
                            numDivisions += durationNum
                            
                        #if note continues into next measure
                        else:
                            durationNum = round(((downbeats[i+1]-note.start)/measureLength)*dpm)
                            noteType = get_note_type(durationNum)
                            notes = create_note(noteName, durationNum, noteType, True, False, voiceNum)
                            for currentNote in notes:
                                measure.append(currentNote)
                            numDivisions += durationNum

                    #if note started in previous measure and continues into this measure
                    #(note starts before downbeat of current measure) and (note does not end before or on downbeat of this measure)
                    elif round(((note.start-downbeats[i])/measureLength)*dpm) < 0 and round(((note.end-downbeats[i])/measureLength)*dpm) > 0:
                        isNote = True
                        if numDivisions != 0:
                            backup = ET.SubElement(measure, 'backup')
                            duration = ET.SubElement(backup, 'duration')
                            duration.text = str(numDivisions)
                            numDivisions = 0
                            voiceNum += 1
                        noteName = pretty_midi.note_number_to_name(note.pitch)
                        
                        #if note ends in current measure
                        #(this is last measure) or (note ends on or before next downbeat)
                        if currentMeasure == len(downbeats) or round(((note.end-downbeats[i+1])/measureLength)*dpm) <= 0:
                            durationNum = round(((note.end-downbeats[i])/measureLength)*dpm)
                            noteType = get_note_type(durationNum)
                            notes = create_note(noteName, durationNum, noteType, False, True, voiceNum)
                            for currentNote in notes:
                                measure.append(currentNote)
                            numDivisions = round(((note.end-downbeats[i])/measureLength)*dpm)
                            
                        #if note continues into next measure
                        else:
                            durationNum = dpm
                            noteType = get_note_type(durationNum)
                            notes = create_note(noteName, durationNum, noteType, False, False, voiceNum)
                            for currentNote in notes:
                                measure.append(currentNote)
                            numDivisions = dpm
                            
                #if there was no note in this measure, a rest is created
                if isNote == False:
                    currentNote = ET.SubElement(measure, 'note')
                    ET.SubElement(currentNote, 'rest')
                    duration = ET.SubElement(currentNote, 'duration')
                    duration.text = str(dpm)
                    #note type
                    if get_note_type(dpm) != 'none':
                        note_type = ET.SubElement(currentNote, 'type')
                        if get_note_type(dpm).find('double_dotted_') != -1:
                            note_type.text = get_note_type(dpm)[14:]
                            ET.SubElement(currentNote, 'dot')
                            ET.SubElement(currentNote, 'dot')
                        elif get_note_type(dpm).find('dotted_') != -1:
                            note_type.text = get_note_type(dpm)[7:]
                            ET.SubElement(currentNote, 'dot')
                        else:
                            note_type.text = get_note_type(dpm)

                i += 1
            instNum += 1
    if filename.find('.xml') == -1 and filename.find('.mxl') == -1 and filename.find('.musicxml') == -1:
        filename += '.xml'
    tree.write(filename, 'UTF8')
