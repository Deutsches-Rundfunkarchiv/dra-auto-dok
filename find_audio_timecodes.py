class find_audio_timecodes():
     
    def __init__(self):
          pass
    
         
    def find_word_in_transcript(self, word,transcript_list,start_audio_list):
        """Utility for combining word with start_times of audio to make them ansteuerbar
        
        Args:
            word(str): Single word or combination of words that should be located in the transcript.
            transcript_list (list): List of sentences that the transcript is divided in and that correspond with the timecodes in the start_audio_list
            start_audio_list (list): List of strat timecodes of single parts from transcript_list. Corresponds with transcript_list.

        Returns:
            start_audio(list): List of timecodes of starting points of the audio where search term (word) appears in.
        
        """
        
        
        start_audio = []

        start_audio_word_ebene = []
        for j in range(len(transcript_list)):
            #print('DEBUG Transcript-Suche word:', word)
            #print('DEBUG Transcript-Suche transcript_list[j]:', transcript_list[j])
            if word != None and transcript_list[j] != None:
                if word.lower() in transcript_list[j].lower() and start_audio_list[j] not in start_audio_word_ebene:
                        
                        start_audio_word_ebene.append(start_audio_list[j])
        start_audio.append(start_audio_word_ebene)

        return(start_audio)

