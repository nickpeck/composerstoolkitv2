from composerstoolkit import *

pf = pitches.PitchFactory()
init_midi()

class MidiInput:
    def __init__(self, gater_func=lambda context: False):
        self.gater_func = gater_func
        self.active_notes = []
        self.control_data = {}
        listener = MidiListener(
            get_midi_device_id("V61"),
            note_on=self.on_note_on,
            note_off=self.on_note_off,
            control_change=self.on_control_change)
        listener.setDaemon(True)
        listener.start()

    def on_note_on(self, e):
        self.active_notes.append(e.data1)

    def on_note_off(self, e):
        self.active_notes.remove(e.data1)

    def on_control_change(self, e):
        self.control_data[e.status] = e.data1

    def __call__(self, context) -> bool:
        return self.gater_func(self)



ostinato = Sequence.from_generator(random_slice(
    Sequence(events=[
        Event(pitches=[pf("C6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("D6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("E6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("G6")], duration=EIGHTH_NOTE),
        Event(pitches=[pf("A6")], duration=EIGHTH_NOTE),
    ])
)).transform(
    loop()
)
    
mysequencer = Sequencer(bpm=100, debug=True)\
    .add_sequence(ostinato, channel_no=1)\
    .add_transformer(gated(
        modal_quantize(scales.E_major),
        MidiGate(lambda context: 40 in context.active_notes),
        lambda: mysequencer.context))\
    # .add_transformer(gated(
    #     modal_quantize(scales.Ab_major),
    #     MyGate(lambda context: 40 in context.active_pitches),
    #     lambda: mysequencer.context))

mysequencer.playback()
