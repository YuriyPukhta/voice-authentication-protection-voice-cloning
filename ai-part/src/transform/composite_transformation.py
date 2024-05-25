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
