from magenta.music import musicxml_reader
import magenta.music
import pretty_midi

def read_from_xml(xml_data):
    """Reads an xml file into a prettyMIDI object.

    Args:
    xml_data : str
        path to a musicxml file

    Returns:
        a prettyMIDI object
    """
    xml_note_sequence = musicxml_reader.musicxml_file_to_sequence_proto(xml_data)
    return magenta.music.sequence_proto_to_pretty_midi(xml_note_sequence)