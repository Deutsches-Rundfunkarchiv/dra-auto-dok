from just_playback import Playback
import datetime
#https://github.com/cheofusi/just_playback


class audio_playback():
    """Playback of source audio files"""

    def __init__(self, audiofile_path):
        self.playback = Playback() # creates an object for managing playback of a single audio file
        self.load_file = self.playback.load_file(audiofile_path)

    def play_file(self):
        self.playback.play() # plays loaded audio file from the beginning

    def pause_playback(self):
        self.playback.pause() # pauses playback. No effect if playback is already paused

    def resume_playback(self):
        self.playback.resume() # resumes playback. No effect if playback is playing

    def stop_playback(self):
        self.playback.stop() # stops playback. No effect if playback is not active

    def scroll_playback_to_second(self, seconds):
        self.playback.seek(seconds) # Spult um "Seconds" vor

    def get_duration(self):
        duration = self.playback.duration
        return(duration)
    
    def get_position(self):
        position = self.playback.curr_pos #returns current position of audioplaying within file
        return(position)
    
    def format_time(self, seconds):
        time_string = str(datetime.timedelta(seconds=int(seconds)))
        return (time_string)
    
    def is_playing(self):
        if self.playback.playing == True:
            status = True
        else:
            status = False
        return (status)
     
     #Not needed for now:
    #
    
   # def deformat_time(self, formated_time):
       # deformat = formated_time.split(':')
       # minutes = int(deformat[0])
       # seconds = int(deformat[1])
       # seconds_all = (minutes *60)+seconds
        #return(seconds_all)
   
    #def set_new_position(self, seconds):
        #self.playback.play()
       # self.playback.seek(seconds) # scrolls player to new position

   
    #def format_time(seconds):
        #minutes, seconds = divmod(seconds, 60)
        #return f'{int(minutes):02d}:{int(seconds):02d}'