from . synth import Playback

class PitchTracker(Playback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_pitches = []

    def noteon(self, track: int, pitch: int, velocity: int):
        self.active_pitches.append((pitch, track))

    def noteoff(self, track: int, pitch: int):
        try:
            self.active_pitches.remove((pitch, track))
        except ValueError:
            pass

    def control_change(self, track: int, cc: int, value: int):
        pass

    def __iter__(self):
        return (item for item in self.active_pitches)

    def __repr__(self):
        return str(self.active_pitches)

    def __len__(self):
        return len(self.active_pitches)

    def __getitem__(self, item):
        return self.active_pitches[item]

    def __enter__(self):
        self.active_pitches = []
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.active_pitches = []
