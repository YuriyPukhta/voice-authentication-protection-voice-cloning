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

class SiameseNetwork(nn.Module):
    def __init__(self):
        super(SiameseNetwork, self).__init__()
        self.conv_layers = nn.Sequential(
                nn.Conv2d(1, 32, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Conv2d(32, 64, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Conv2d(64, 128, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Conv2d(128, 256, kernel_size=3),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.fc_layers = nn.Sequential(
                nn.Linear(4608, 1024),
                nn.ReLU(inplace=True),
        )

        self.final = nn.Linear(1024, 2)

    def forward_once(self, x):

        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        x = self.fc_layers(x)
        return x

    def forward(self, input1, input2):
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)
        return self.final(torch.abs(output1 - output2))


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
        samples = torch.from_numpy(samples).type(torch.float32)
        spec = self.mel_spectrogram(samples)
        spec = self.amplitude_to_db(spec)
        if self.normalize:
            mean = [0.5]
            std = [0.5]
            spec = normalize(spec, mean, std)
        spec = spec.unsqueeze(0)
        return (spec)


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
        return (samples,  self.target_sample_rate)
'''
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

        elif sample_length < target_samples_length:
            record = np.zeros((self.replay, sample_rate*self.duration_seconds))
            for time in range(self.replay):
                pad_begin_len = np.random.randint(
                    0, target_samples_length - sample_length)
                pad_end_len = target_samples_length - sample_length - pad_begin_len
                pad_width = (pad_begin_len, pad_end_len)
                sample_pad=np.pad(samples, pad_width, self.padding_mode)
                record[time, :] = self.shift_transform(sample_pad, sample_rate)
            return record

        elif sample_length > target_samples_length:
            record = np.zeros((self.replay, sample_rate*self.duration_seconds))
            step=(samples.shape[-1] - self.duration_seconds * sample_rate ) / self.replay
            pad_begin_len = 0
            time = 0
            while pad_begin_len < samples.shape[-1] - target_samples_length:

                record[time, :] = samples[..., pad_begin_len: pad_begin_len + target_samples_length]
                pad_begin_len += step
                time += 1
            return record
'''

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
            return samples

        elif sample_length > target_samples_length:
            if self.padding_direction == "start":
                start = 0
            elif self.padding_direction == "end":
                start = sample_length - target_samples_length
            else:
                start = np.random.randint(
                    0, sample_length - target_samples_length)

            return samples[..., start: start + target_samples_length]

        elif sample_length < target_samples_length:
            if self.padding_direction == "start":
                pad_width = (target_samples_length - sample_length, 0)
            elif self.padding_direction == "end":
                pad_width = (0, target_samples_length - sample_length)
            else:
                pad_begin_len = np.random.randint(
                    0, target_samples_length - sample_length)
                pad_end_len = target_samples_length - sample_length - pad_begin_len
                pad_width = (pad_begin_len, pad_end_len)

            return np.pad(samples, pad_width, self.padding_mode)

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
    model = SiameseNetwork()
    model.load_state_dict(torch.load("./model/combined_cnn_mix.pt"))
    model.eval()
    return model


def get_data(file):
    SAMPLE_RATE = 16000
    audio, sample_rate = sf.read(file)
    audio = np.array(audio)
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
        anchor_sgram = torch.unsqueeze(anchor_batch, 0).to("cuda")
        posneg_sgram = torch.unsqueeze(target_batch, 0).to("cuda")
        output = model(anchor_sgram, posneg_sgram)
        predictions.append(torch.argmax(output).cpu().item())
    predictions = sum(predictions) / anchor_batch.shape[-1]
    return predictions
