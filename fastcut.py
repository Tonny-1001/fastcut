from moviepy.editor import VideoFileClip, concatenate_videoclips
import numpy as np
import os


def clear_console():
    command = "clear"
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)


def is_silent(audio_array, threshold=0.005):
    return np.mean(np.abs(audio_array)) < threshold


def is_too_loud(audio_array, threshold=0.09):
    return np.mean(np.abs(audio_array)) > threshold


def calculate_average_frequency(audio_data):
    # If the audio chunk is stereo, convert it to mono
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)  # Convert to mono by averaging channels

    # Perform FFT on the audio chunk
    fft_result = np.fft.fft(audio_data)
    magnitudes = np.abs(fft_result)
    frequencies = np.fft.fftfreq(len(audio_data), 1 / 44100)

    # Consider only positive frequencies
    positive_freq_indices = np.where(frequencies >= 0)
    magnitudes = magnitudes[positive_freq_indices]
    frequencies = frequencies[positive_freq_indices]

    # Calculate the average frequency weighted by magnitudes
    average_frequency = np.sum(magnitudes * frequencies) / np.sum(magnitudes)
    # return average_frequency
    print(f"{average_frequency:.2f} Hz")
    # return average_frequency


def edit_file(file_path, output_filename, min_silence_to_cut_duration):
    clear_console()
    print("Starting...")

    video = VideoFileClip(file_path)
    audio = video.audio

    # Parameters
    sample_rate = 44100  # Sampling rate
    chunk_duration = 0.05  # Duration of each chunk in seconds

    # Split the audio into chunks and analyze for silence
    start_time = 0

    splitted_to_chunks = []
    while start_time < audio.duration:
        end_time = start_time + chunk_duration
        audio_chunk = audio.subclip(start_time, end_time).to_soundarray(fps=sample_rate)

        if is_silent(audio_chunk):
            splitted_to_chunks.append([round(start_time, 2), True])
            print(f"Current moment: {start_time:.2f} is silent")
        else:
            splitted_to_chunks.append([round(start_time, 2), False])
            print(f"Current moment: {start_time:.2f} is NOT silent")
        start_time += chunk_duration

    clear_console()
    print("Clearing anomalies...")
    # usuwamy pojedyncze anomalie:
    for i in range(len(splitted_to_chunks)):
        if splitted_to_chunks[i][1]:
            if not splitted_to_chunks[i-1][1] and not splitted_to_chunks[i+1][1]:
                splitted_to_chunks[i][1] = False
        else:
            if splitted_to_chunks[i-1][1] and splitted_to_chunks[i+1][1]:
                splitted_to_chunks[i][1] = True

    clear_console()
    print("Searching matching silence chunks...")
    silence_chunks_list = []

    silence_duration = 0
    silence_start_time = 0
    counter = 0
    for chunk in splitted_to_chunks:
        if chunk[1]:
            if counter+1 == len(splitted_to_chunks):
                silence_chunks_list.append(
                    (round(silence_start_time, 2), round(silence_start_time + silence_duration, 2)))
                break
            if silence_start_time == 0:
                silence_start_time = chunk[0]
            silence_duration += chunk_duration
        else:
            if silence_duration == 0:
                counter += 1
                continue
            silence_chunks_list.append((round(silence_start_time, 2), round(silence_start_time + silence_duration, 2)))
            silence_duration = 0
            silence_start_time = 0
        counter += 1

    chunks_to_delete = []
    for chunk_elem in silence_chunks_list:
        if chunk_elem[1] - chunk_elem[0] >= min_silence_to_cut_duration:
            print(f"{chunk_elem} - TO DELETE")
            chunks_to_delete.append(chunk_elem)
        else:
            print(chunk_elem)

    clear_console()

    total_silence = 0
    for elem in chunks_to_delete:
        total_silence += (elem[1] - elem[0])
    print("File was analyzed! Results:")
    print(f"Total silence length to delete: {total_silence:.2f}sec")
    if video.duration-total_silence < 60:
        print(f"Video length after edits: {round(video.duration - total_silence, 2)}sec")
    else:
        print(f"Video length after edits: {round((video.duration-total_silence)/60)}min")
    if input("Continue? (y/n): ") == "y":
        pass
    else:
        print("Ok!")
        return
    print("Combining...")

    # Create a list of non-silent video clips
    keep_intervals = []
    last_end = 0

    for start, end in chunks_to_delete:
        if last_end < start:
            keep_intervals.append((last_end, start))
            # if last_end < chunk_duration:
            #     keep_intervals.append((last_end, start+chunk_duration))
            # else:
            #     keep_intervals.append((last_end - chunk_duration, start + chunk_duration))
        last_end = end

    # Add the final segment if there is any video left after the last interval
    if last_end < video.duration:
        keep_intervals.append((last_end, video.duration))

    # Extract the clips to keep
    clips = [video.subclip(start, end) for start, end in keep_intervals]

    # Concatenate the clips into a single video
    final_clip = concatenate_videoclips(clips)

    clear_console()
    print("Saving...")
    # Save the result
    if ".mp4" not in output_filename:
        output_filename += ".mp4"
    final_clip.write_videofile(output_filename)
    clear_console()
    print("All done!")
    input("Press enter to close...")


if __name__ == '__main__':
    print("Welcome to fastcut!")
    print(
        """
    Options:
    1 - Clear silence moments.
    2 - Change frame rate.
        """
    )
    choice = input(">>> ")
    if choice == "1":
        file = input("Enter file path: ")
        output_name = input("Enter output file name: ")
        max_silence_tile = int(input("Enter max silence duration (recommended 2-4): "))
        edit_file(file, output_name, max_silence_tile)
