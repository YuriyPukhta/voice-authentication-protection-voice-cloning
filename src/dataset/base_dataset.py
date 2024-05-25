import librosa

from src.columns.base_dataset_column import DatasetColumn
from src.transform.transform import CustomAdjustDurationTransform, ResampleTransform, ToMelSpectrogramTransform
import torch
from torch.utils.data import Dataset

from src.transform.composite_transformation import CompositeTransformation


class BaseSoundDS(Dataset):
    def __init__(
        self,
        voiceDataset,
        voice_data_path,
        sample_rate=16000,
        duration=3,
        transform=None
    ):
        self.voiceDataset = voiceDataset
        self.voice_data_path = str(voice_data_path)
        self.duration = duration
        self.sample_rate = sample_rate
        self.transform = None
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

    def __len__(self):
        return len(self.voiceDataset)

    def _get_sgram(self, audio_file):
        audio, sample_rate = librosa.load(audio_file, sr=self.sample_rate)
        spectrogram = self.transform.transform((audio, sample_rate))
        return spectrogram

    def _get_sample_path(self, path):
        return self.voice_data_path + path

    def _get_label(self, label):
        return torch.tensor(1 if label else 0, dtype=torch.int64)

    def __getitem__(self, idx):
        anchor_path, posneg_path, _, _, label = self.voiceDataset.iloc[idx][
            [
                DatasetColumn.ANCHOR_PATH,
                DatasetColumn.POSNEG_PATH,
                DatasetColumn.ANCHOR_ID,
                DatasetColumn.POSNEG_ID,
                DatasetColumn.LABEL
            ]
        ].values.tolist()

        anchor_file = self._get_sample_path(anchor_path)
        posneg_file = self._get_sample_path(posneg_path)
        label = self._get_label(label)
        anchor_sgram = self._get_sgram(anchor_file)
        posneg_sgram = self._get_sgram(posneg_file)

        return anchor_sgram, posneg_sgram, label
