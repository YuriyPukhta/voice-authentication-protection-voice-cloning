# voice-authentication-protection-voice-cloning
voice authentication taking into consideration the risks of voice cloning.

## Experiment
There two sub models for Siamese network
* CNN 
* LSTM

Experiment with CNN file
1. ```train_base_cnn.ipynb``` baseline train for recognition  whether the voice belong to the same person
2. ```train_generated_cnn.ipynb``` training to recognize whether a person's voice is an original or a generated voice based on a voice cloning model
3. ```train_combined_cnn.ipynb``` combines learning to recognize other people's voices and generated ones


Experiment with LSTM file
1. ```train_base_cnn.ipynb``` baseline train for recognition  whether the voice belong to the same person
2. ```train_generated_cnn.ipynb``` training to recognize whether a person's voice is an original or a generated voice based on a voice cloning model
2. ```train_combined_cnn.ipynb``` combines learning to recognize other people's voices and generated ones


In ```mix``` directory present experiment with dataset mixing during training

## Dateset
Dataset Mozilla Common Voice

### Reproduce Data
1. Download dataset
2. Move it to ```data``` directory
3. generate voice with ```generate_voice_tsv.ipynb``` get file ```generated.tsv```
4. Generate cloned voice with ```generate_voice_xtts_v2.py``` with ```generated.tsv```
5. (Optional) Resample audio ```resampling.ipynb```

### Reproduce Dateset
Run scripts directory in ```data_generation```
