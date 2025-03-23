# Convert a folder of wav files to flac files
# Usage: python wav2flac.py <input_folder> <output_folder> <extension>
# Example: python wav2flac.py /home/username/wav /home/username/flac

import os
import sys
import torchaudio
import tqdm

def wav2x(input_folder, output_folder, extension='flac'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, _, files in os.walk(input_folder):
        for file in tqdm.tqdm(files):
            if file.endswith('.wav'):
                wav_file = os.path.join(root, file)

                # Compute relative path and create corresponding output folder
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)

                # Save output file in the corresponding subfolder
                flac_file = os.path.join(output_subfolder, file.replace('.wav', f'.{extension}'))
                waveform, sample_rate = torchaudio.load(wav_file)
                torchaudio.save(flac_file, waveform, sample_rate=sample_rate)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python wav2x.py <input_folder> <output_folder> <extension>')
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    extension = sys.argv[3] if len(sys.argv) > 3 else 'flac'

    wav2x(input_folder, output_folder, extension)
    print('Conversion completed!')
