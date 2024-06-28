import numpy as np
from modules.useful_functions import clear_console
from modules.delete_silence import delete_silence


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


if __name__ == '__main__':
    while True:
        clear_console()
        print("Welcome to fastcut!")
        print(
            """
        Options:
        0 - Exit.
        1 - Clear silence moments.
        2 - Change frame rate.
            """
        )
        choice = input(">>> ")
        if choice == "1":
            file = input("Enter file path: ")
            while file == "":
                file = input("Enter file path: ")

            output_name = input("Enter output file name: ")
            if output_name == "":
                output_name = "output.mp4"

            max_silence_tile = input("Enter max silence duration (recommended 2-4): ")
            if max_silence_tile == "":
                max_silence_tile = 2
            try:
                max_silence_tile = int(max_silence_tile)
            except ValueError:
                print("Enter a number!!")

            padding = input("Do you want to apply padding to cut out clips? (y/n): ")
            while padding not in ["y", "n", ""]:
                padding = input("Do you want to apply padding to cut out clips? (y/n): ")
                if padding == "":
                    padding = "y"

            delete_silence(file, output_name, max_silence_tile, padding=padding)
            input("Edited file was saved successfully.\nPress enter...")
        elif choice == "2":
            pass
        elif choice == "0":
            print("Ok!")
            break

