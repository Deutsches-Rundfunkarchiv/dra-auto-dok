import PySimpleGUI as sg
import threading
import time
from audioplayer import audio_playback
import tkinter as tk  # Import tkinter for font metrics

def format_transcript(transcript_lines, timecodes):
    """Formats transcript with timecodes for display."""
    formatted_text = ""
    for i, line in enumerate(transcript_lines):
        timecode_str = time.strftime('%H:%M:%S', time.gmtime(timecodes[i]))  # Format timecode to HH:MM:SS
        formatted_text += f"{timecode_str}: {line}\n"
    return formatted_text

def highlight_current_line(window, current_time, timecodes):
    """Highlights the current line and removes highlight from previous lines."""
    window['-TRANSCRIPT-'].update(background_color='white')

    for i, start_time in enumerate(timecodes):
        window['-TRANSCRIPT-'].Widget.tag_remove("highlight", f"{i+1}.0", f"{i+1}.end")

        if i + 1 < len(timecodes) and start_time <= current_time < timecodes[i + 1]:
            window['-TRANSCRIPT-'].Widget.tag_add("highlight", f"{i+1}.0", f"{i+1}.end")
            window['-TRANSCRIPT-'].Widget.tag_configure("highlight", background="yellow")

            # Calculate pixel height of font
            font_string = window['-TRANSCRIPT-'].Widget.cget("font")
            font = tk.font.Font(font=font_string)  # Create a Tkinter font object
            font_height = font.metrics('linespace') # Returns a reliable pixel value of font height.

            num_lines = len(timecodes)
            window_height = window['-TRANSCRIPT-'].Widget.winfo_height()
            visible_lines = window_height // font_height

            scroll_to_line = max(0, i - visible_lines // 2)  # Calculate line to scroll to
            window['-TRANSCRIPT-'].set_vscroll_position(scroll_to_line / num_lines)

            return
        elif i + 1 == len(timecodes) and current_time >= timecodes[i]: # last line
            window['-TRANSCRIPT-'].Widget.tag_add("highlight", f"{i+1}.0", f"{i+1}.end")
            window['-TRANSCRIPT-'].Widget.tag_configure("highlight", background="yellow")

            if i > 0: # Remove highlight from previous line only if not the first line
                window['-TRANSCRIPT-'].Widget.tag_remove("highlight", f"{i}.0", f"{i}.end")

            window['-TRANSCRIPT-'].set_vscroll_position(max(0,(i-1)/ len(timecodes)))
            return

def transcript_player(audio_file, transcript_lines, timecodes, audio_file2):
    """Plays audio and displays/highlights the transcript."""

    player = audio_playback(audio_file)
    duration = player.get_duration()
    formatted_transcript = format_transcript(transcript_lines, timecodes)

    player2 = audio_playback(audio_file2)
    duration2 = player2.get_duration()

    layout = [
        [sg.Text("Transcript Player", background_color = 'black', font=('Arial Bold', 20), pad=(5, (50, 10)))],
        [sg.Text("(Audio Pre-Processed ohne Musik, verminderte Geräuschpassagen etc.)", background_color = 'black', font=('Arial Bold', 12))],
        [sg.Multiline(formatted_transcript, size=(80, 20), key='-TRANSCRIPT-', font=('Arial', 12), disabled=True, enable_events=True, background_color = 'white')],
        [sg.Slider((0, duration), orientation='h', key='-SLIDER-', enable_events=True, disable_number_display=True, size=(60, 20)),
         sg.Text(time.strftime('%H:%M:%S', time.gmtime(0)), key='-CURRENT_TIME-')], # Initial time display
        [sg.Button("Play"), sg.Button("Pause"), sg.Button("Stop")],
        [sg.HorizontalSeparator()],  # Separator between players
        [sg.Text("Gesamtes File mit Musik, Noise, etc.", background_color = 'black', font=('Arial Bold', 20), pad=(5, (50, 10)))],
        [sg.Slider((0, duration2), orientation='h', key='-SLIDER2-', enable_events=True, disable_number_display=True, size=(60, 20)),
         sg.Text(time.strftime('%H:%M:%S', time.gmtime(0)), key='-CURRENT_TIME2-')],
        [sg.Button("Play 2"), sg.Button("Pause 2"), sg.Button("Stop 2")]
    ]

    window = sg.Window("Transcript Player", layout, finalize=True, resizable=True) # Make window resizable

    playing = False  # Flag to track playback state
    paused = False
    playing2 = False
    paused2 = False
    seeking2 = False

    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED:
            break

        if event == "Play":
            if playing2: # Stop player2 if it was running
                player2.stop_playback()
                playing2 = False
                paused2 = False
                window['-CURRENT_TIME2-'].update(player2.format_time(0))
                window['-SLIDER2-'].update(0)

            seek_time = int(values['-SLIDER-'])
            if not playing:
                if paused:
                    player.resume_playback()
                    paused = False
                else:
                    player.play_file()
                playing = True
                seeking = False # Reset seeking flag when playback starts
                threading.Thread(target=update_transcript, args=(window, player, timecodes, duration, seeking), daemon=True).start()
            # This else-block handles seeking while playing
            else:
                seeking = True
                player.scroll_playback_to_second(int(values['-SLIDER-']))
                highlight_current_line(window, int(values['-SLIDER-']), timecodes)  # Directly update highlight during seek

        elif event == "Pause":
            seek_time = int(values['-SLIDER-'])
            if playing:
                player.pause_playback()
                playing = False
                paused = True
                highlight_current_line(window, seek_time, timecodes)

        if event == "Stop":
            seek_time = int(values['-SLIDER-'])
            if playing or paused: # only stop if player is active
                player.stop_playback()
                playing = False
                paused = False

            window['-SLIDER-'].update(value = 0)
            window['-CURRENT_TIME-'].update(player.format_time(0))
            window['-TRANSCRIPT-'].update(background_color='white')
            highlight_current_line(window, seek_time, timecodes)


        elif event == '-SLIDER-': # Handle slider events separately
            seeking = True  # Set seeking flag when slider is moved
            seek_time = int(values['-SLIDER-'])
            player.scroll_playback_to_second(seek_time)
            window['-CURRENT_TIME-'].update(player.format_time(seek_time))# Update Current time Display, Divide by 1000 because format expects time in seconds instead of milliseconds.
            highlight_current_line(window, seek_time, timecodes)

        # Player 2 controls (mirrored logic from Player 1)
        elif event == "Play 2":
            if playing:# Stop player1 if it was playing
                player.stop_playback()
                playing = False
                paused = False
            if not playing2:
                if paused2:
                    player2.resume_playback()
                    paused2 = False
                else:
                    player2.play_file()
                playing2 = True
                seeking2 = False # Reset seeking flag when playback starts
                threading.Thread(target=update_player_without_transcript, args=(window, player2, duration, seeking2), daemon=True).start()
            else:
                seeking2 = True
                player2.scroll_playback_to_second(int(values['-SLIDER-']))
        
        elif event == "Pause 2":
            seek_time = int(values['-SLIDER2-'])
            if playing2:
                player2.pause_playback()
                playing2 = False
                paused2 = True
                
        if event == "Stop 2":
            seek_time = int(values['-SLIDER2-'])
            if playing2 or paused: # only stop if player is active
                player2.stop_playback()
                playing2 = False
                paused2 = False

            window['-SLIDER2-'].update(value = 0)
            window['-CURRENT_TIME2-'].update(player2.format_time(0))


        elif event == '-SLIDER2-': # Handle slider events separately
            seeking = True  # Set seeking flag when slider is moved
            seek_time = int(values['-SLIDER2-'])
            player2.scroll_playback_to_second(seek_time)
            window['-CURRENT_TIME2-'].update(player2.format_time(seek_time))# Update Current time Display, Divide by 1000 because format expects time in seconds instead of milliseconds.
 
    window.close()

def update_transcript(window, player, timecodes, duration, seeking):
    """Updates the highlighted line and current time during playback."""
    while player.is_playing():
        if not seeking:
            current_time = player.get_position()  # Get the current position from audioplayer

            # Format current time using player's format_time method
            formatted_time = player.format_time(current_time)

            window['-CURRENT_TIME-'].update(value=formatted_time) # Update the UI element
            window['-SLIDER-'].update(current_time)

            highlight_current_line(window, current_time, timecodes)

        time.sleep(0.1)

def update_player_without_transcript(window, player, duration, seeking):
    """Updates the highlighted line and current time during playback."""
    while player.is_playing():
        if not seeking:
            current_time = player.get_position()  # Get the current position from audioplayer

            # Format current time using player's format_time method
            formatted_time = player.format_time(current_time)

            window['-CURRENT_TIME2-'].update(value=formatted_time) # Update the UI element
            window['-SLIDER2-'].update(current_time)

        time.sleep(0.1)

