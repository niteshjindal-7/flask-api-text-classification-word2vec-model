from pydub import AudioSegment
import math
from pydub.silence import split_on_silence


class SplitWavAudioMubin():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder  + "/" + filename
        
        self.audio = AudioSegment.from_wav(self.filepath)
    
    def get_duration(self):
        return self.audio.duration_seconds
    
    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + "/" + split_filename, format='wav')
        
    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + "_" + self.filename
            self.single_split(i, i+min_per_split, split_fn)
            print(str(i) +  "Done")
            if i == total_mins - min_per_split:
                print("All splited successfully")


#test2
folder= "/home/nitesh/Documents/AMPBA/AISPRY/Processed_Audio_Files"
#file= "Lecture_03__Hypothesis_Space_and_Inductive_Bias.wav"
file="Lecture_03__Hypothesis_Space_and_Inductive_Bias.wav"

def remove_silence_from_audio(folder, file):
    sound = AudioSegment.from_file(folder  + "/" + file, format = "wav")
    audio_chunks = split_on_silence(sound, min_silence_len = 1500, silence_thresh = -45, keep_silence = 50)
    for i, chunk in enumerate(audio_chunks):
        split_fn = folder + "/Splitted_Audio_Files/" + str(i) + "_" + file
        # output_file =  "/home/nitesh/Documents/AMPBA/AISPRY/{}".format(split_fn)
        output_file=split_fn
        print("Exporting file", output_file)
        chunk.export(output_file, format="wav")

remove_silence_from_audio(folder, file)

#test3
folder= "/home/nitesh/Documents/AMPBA/AISPRY/Processed_Audio_Files"
file= "Lecture_03__Hypothesis_Space_and_Inductive_Bias.wav"
split_wav = SplitWavAudioMubin(folder, file)
split_wav.multiple_split(min_per_split=1)