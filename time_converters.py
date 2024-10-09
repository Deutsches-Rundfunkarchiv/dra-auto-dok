def convert_milliseconds_to_time_format(input_milliseconds):
    """Converts Milliseconds to time format that can be used in HFDB with les processing
    
    Args:
        input_milliseconds(int/str): Milliseconds amount that should be converted to time format. Could be string or int as input because string would be converted in class algorithm.

    Returns
        "%d:%d:%d" % (hours, minutes, seconds): Standard python time format in "hours:minutes:seconds" for input.
    
    """
    millis=input_milliseconds
    millis = int(millis)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24

    #print ("%d:%d:%d" % (hours, minutes, seconds))
    return("%d:%d:%d" % (hours, minutes, seconds))

#Converter - Stunden-Zeitformat zurück in Millisekunden
def convert_to_ms(input):
    """Converts Python time format to milliseconds
    Args:
        input(str): Time string in standard time format

    Returns:
        milliseconds(int): Amount of milliseconds represented by input.
    """
    s = input
    hours, minutes, seconds = (["0", "0"] + s.split(":"))[-3:]
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
    return(miliseconds)

def convert_to_ms_yamnet(input):
    """Converts time format given in YAMnet sources to milliseconds.
    
    Args:
       input(str): Time string given in YAMNet export format

    Returns:
       milliseconds(int): Amount of millisenconds represented by input. 
    """
    s = input
    hours, minutes, seconds = (["0", "0"] + s.split(":"))[-3:]
    hours = int(hours)
    minutes = int(minutes)
    seconds = seconds.split('.')[0]
    seconds = int(seconds)
    miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
    return(miliseconds)