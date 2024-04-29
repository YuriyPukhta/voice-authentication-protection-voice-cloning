
import random


from numpy.typing import NDArray
import numpy as np
import torch
import librosa
from torchaudio import transforms
from audiomentations import AirAbsorption, RoomSimulator, Shift, SevenBandParametricEQ
from torchvision.transforms.functional import normalize


class ToMelSpectrogramTransform:
    def __init__(
            self,
            sample_rate=None,
            n_mels=64,
            n_fft=1024,
            hop_len=None,
            top_db=80,
            normalize=False
    ):
        self.mel_spectrogram = transforms.MelSpectrogram(
            sample_rate, n_fft=n_fft, hop_length=hop_len, n_mels=n_mels)
        self.amplitude_to_db = transforms.AmplitudeToDB(top_db=top_db)
        self.normalize = normalize

    def __call__(self, samples: NDArray[np.float32], _: int):
        samples = torch.from_numpy(samples)
        spec = self.mel_spectrogram(samples)
        spec = self.amplitude_to_db(spec)
        if self.normalize:
            mean = [0.5]
            std = [0.5]
            spec = normalize(spec, mean, std)

        return (spec)

class AudioToTimeSeriesTransform:
    def __init__(
            self,
            n_fft,
            hop_len=None,
            win_length=None,
            top_db=80,
            normalize=False
    ):
        self.spectrogram = transforms.Spectrogram(
            n_fft,
            win_length=win_length,
            hop_length=hop_len,
        )
        self.amplitude_to_db = transforms.AmplitudeToDB(top_db=top_db)
        self.normalize = normalize

    def __call__(self, samples: NDArray[np.float32], _: int):
        samples = torch.from_numpy(samples)
        spec = self.spectrogram(samples)
        spec = self.amplitude_to_db(spec)
        spec = spec.permute(1, 0)
        spec = spec.squeeze(0)
        return (spec)

class CustomAdjustDurationTransform:
    def __init__(
            self,
            duration_seconds: float = None,
            padding_mode="silence",
            padding_direction=None
    ):
        assert padding_direction in ["start", "end", None]

        if padding_mode == "silence":
            padding_mode = "constant"
        self.padding_direction = padding_direction
        self.duration_seconds = duration_seconds
        self.padding_mode = padding_mode

    def __call__(self, samples: NDArray[np.float32], sample_rate: int):
        target_samples_length = int(self.duration_seconds * sample_rate)
        sample_length = samples.shape[-1]

        if sample_length == target_samples_length:
            return (samples, sample_rate)

        elif sample_length > target_samples_length:
            if self.padding_direction == "start":
                start = 0
            elif self.padding_direction != "end":
                start = sample_length - target_samples_length
            else:
                start = np.random.randint(
                    0, sample_length - target_samples_length)

            return (samples[..., start: start + target_samples_length], sample_rate)

        elif sample_length < target_samples_length:
            if self.padding_direction == "start":
                pad_width = (target_samples_length - sample_length, 0)
            elif self.padding_direction != "end":
                pad_width = (0, target_samples_length - sample_length)
            else:
                pad_begin_len = random.randint(
                    0, target_samples_length - sample_length)
                pad_end_len = target_samples_length - sample_length - pad_begin_len
                pad_width = (pad_begin_len, pad_end_len)

            return (np.pad(samples, pad_width, self.padding_mode), target_samples_length)


class ResampleTransform:
    def __init__(
            self, target_sample_rate: int
    ):
        self.target_sample_rate = target_sample_rate

    def __call__(self, samples: NDArray[np.float32], sample_rate: int):
        samples = librosa.core.resample(
            samples,
            orig_sr=sample_rate,
            target_sr=self.target_sample_rate
        )
        return (samples, sample_rate)


class ShiftWrapperTransform:
    def __init__(
            self,
            min_shift=0.2,
            max_shift=0.2
    ):
        self.shift_transform = Shift(min_shift=min_shift, max_shift=max_shift, p=1)

    def __call__(self, samples: NDArray[np.float32], sr: int):
        samples = self.shift_transform(samples, sr)
        return (samples, sr)


class AirAbsorptionWrapperTransform:
    def __init__(
            self,
            min_distance=0.2,
            max_distance=2,
    ):
        self.air_absorption_transform = AirAbsorption(
            min_distance=min_distance,
            max_distance=max_distance,
            p=1.0
        )

    def __call__(self, samples: NDArray[np.float32], sr: int):
        samples = self.air_absorption_transform(samples, sr)
        return (samples, sr)


class RoomSimulatorWrapperTransform:
    def __init__(
            self,
    ):
        self.room_simulator_transform = RoomSimulator(p=1.0)

    def __call__(self, samples: NDArray[np.float32], sr: int):
        samples = self.room_simulator_transform(samples, sr)
        return (samples, sr)


class EqualizerWrapperTransform:
    def __init__(
            self,
            min_gain_db=-10,
            max_gain_db=10,
            p=0.7
    ):
        self.equalizer = SevenBandParametricEQ(
            min_gain_db=min_gain_db, max_gain_db=max_gain_db, p=1.0)

    def __call__(self, samples: NDArray[np.float32], sr: int):
        samples = self.equalizer(samples, sr)
        return (samples, sr)
