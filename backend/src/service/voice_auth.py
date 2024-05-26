from random import random

import numpy as np
import torch
from audiomentations import Shift
from numpy._typing import NDArray
import librosa
from torch import nn
from torchaudio import transforms
from torchvision.transforms.v2.functional import normalize
from virtualenv.activation import batch
import soundfile as sf

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
        for i in samples:
            spec = self.mel_spectrogram(samples)
            spec = self.amplitude_to_db(spec)
            if self.normalize:
                mean = [0.5]
                std = [0.5]
                spec = normalize(spec, mean, std)
            spec = spec.unsqueeze(0)
        return spec

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
        self.replay = 6
        self.shift_transform = Shift(min_shift=-0.5, max_shift=0.5, p = 1)

    def __call__(self, samples: NDArray[np.float32], sample_rate: int):
        target_samples_length = int(self.duration_seconds * sample_rate)
        sample_length = samples.shape[-1]

        if sample_length == target_samples_length:
            record = np.zeros((self.replay, sample_rate*self.duration_seconds))
            for time in range(self.replay):
                record[time, :] = self.shift_transform(samples, sample_rate)
            return record

        elif sample_length > target_samples_length:
            record = np.zeros((self.replay, sample_rate*self.duration_seconds))
            for time in range(self.replay):
                start = np.random.randint(
                        0, sample_length - target_samples_length)
                pad_sample = samples[..., start: start + target_samples_length]
                record[time, :] = self.shift_transform(pad_sample, sample_rate)
                return record

        elif sample_length < target_samples_length:
            record = np.zeros((self.replay, sample_rate*self.duration_seconds))
            step=(samples.shape[-1] - self.duration_seconds * sample_rate ) / self.replay
            pad_begin_len = 0
            time = 0
            while pad_begin_len < samples.shape[-1] - self.duration_seconds * sample_rate:
                pad_end_len = target_samples_length - sample_length - pad_begin_len
                pad_width = (pad_begin_len, pad_end_len)
                pad_begin_len += step
                record[time, :] = np.pad(samples, pad_width, self.padding_mode), target_samples_length
                time += 1

class CompositeTransformation:
    def __init__(self, transformations):
        if len(transformations) <= 0:
            raise ValueError("Can`t be empty")
        self.transformations = transformations

    def transform(self, audio_signal):
        transformed_signal = (audio_signal[0].copy(), audio_signal[1])
        for transformation in self.transformations:

            transformed_signal = transformation(*transformed_signal)
        return transformed_signal


def get_load_model():
    model = torch.load('./model_save/' + "combined_cnn_mix.pt")
    model.eval()
    return model


def get_data(file):
    SAMPLE_RATE = 16000
    audio, sample_rate = sf.read(file)
    resampled_audio, sample_rate = ResampleTransform(target_sample_rate=SAMPLE_RATE)(audio, sample_rate)
    expanded_audio = CustomAdjustDurationTransform(duration_seconds=3)(resampled_audio, sample_rate)
    sgram = ToMelSpectrogramTransform(sample_rate=SAMPLE_RATE, n_mels=64, n_fft=512)(expanded_audio, None)
    return sgram


def validate(anchor, target, device='cuda'):
    model = get_load_model()
    model.to(device)
    predictions = []

    anchor_batch = get_data(anchor)
    target_batch = get_data(target)
    with torch.no_grad():
        for i in range(anchor_batch.shape[-1]):
            anchor_sgram = torch.unsqueeze(anchor_batch[i], 0).to("cuda")
            posneg_sgram = torch.unsqueeze(target_batch[i], 0).to("cuda")
            output = model(anchor_sgram, posneg_sgram)
            predictions.append(torch.argmax(output).cpu().item())
    predictions = sum(predictions) / anchor_batch.shape[-1]

    return predictions