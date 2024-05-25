import librosa

from src.columns.base_dataset_column import DatasetColumn
from src.transform.transform import CustomAdjustDurationTransform, ResampleTransform, ToMelSpectrogramTransform
from torch.utils.data import Dataset
import torch
from src.transform.composite_transformation import CompositeTransformation

class UniversalDS(Dataset):
	def __init__(
		self,
		voice_dataset,
		voice_data_path,
		generated_voice_dataset = None,
		generated_voice_data_path = None,
		sample_rate=16000,
		duration=3,
		transform=None
	):
		self.voice_dataset = voice_dataset
		self.generated_voice_dataset = generated_voice_dataset
		self.voice_data_path = str(voice_data_path)
		self.generated_voice_data_path = str(generated_voice_data_path)
		self.duration = duration
		self.sample_rate = sample_rate
		if transform is not None:
			self.transform = transform
		else:
			self.transform = CompositeTransformation(
				[
					ResampleTransform(target_sample_rate=sample_rate),
					CustomAdjustDurationTransform(duration_seconds=duration),
					ToMelSpectrogramTransform(
						sample_rate=sample_rate, n_mels=64, n_fft=512)
				]
			)
		self.mix_dataset()

	def __len__(self):
		return len(self.temp_dataset)

	def _get_sample(self, audio_file):
		audio, sample_rate = librosa.load(audio_file, sr=self.sample_rate)
		sample = self.transform.transform((audio, sample_rate))
		return sample
	
	def _get_sample_path(self, path, source):
		data_path = self.voice_data_path if source == 'original' else self.generated_voice_data_path
		return data_path + path

	def reset_iteration(self):
		self.iteration_to_mix = len(self.temp_dataset)

	def __getitem__(self, idx):

		anchor_path, posneg_path, anchor_client_id, posneg_client_id, anchor_source, posneg_source = self.temp_dataset.iloc[idx][
			[
				DatasetColumn.ANCHOR_PATH,
				DatasetColumn.POSNEG_PATH,
				DatasetColumn.ANCHOR_ID,
				DatasetColumn.POSNEG_ID,
				DatasetColumn.SOURCE_ANCHOR,
				DatasetColumn.SOURCE_POSNEG,
			]
		].values.tolist()

		anchor_file = self._get_sample_path(anchor_path, anchor_source)
		posneg_file = self._get_sample_path(posneg_path, posneg_source)
		label = self._get_label(anchor_client_id, posneg_client_id, anchor_source, posneg_source)
		anchor_sample = self._get_sample(anchor_file)
		posneg_sample = self._get_sample(posneg_file)
		self.iteration_to_mix -= 1
		if self.iteration_to_mix == 0:
			self.mix_dataset()
		return anchor_sample, posneg_sample, label

	def _get_label(self, anchor_client_id, posneg_client_id, anchor_source, posneg_source):
		label = anchor_client_id == posneg_client_id and anchor_source == posneg_source
		return torch.tensor(1 if label else 0, dtype=torch.int64)
	
	def mix_dataset(self):
		self.reset_iteration()
		pass
