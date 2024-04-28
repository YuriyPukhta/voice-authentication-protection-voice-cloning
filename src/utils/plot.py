import matplotlib.pyplot as plt


def plot(sample):
    def plot_spec(ax, spec, title):
        ax.set_title(title)
        ax.imshow(spec[0], origin="lower", aspect="auto")

    fig, axes = plt.subplots(2, 1, sharex=True, sharey=True)
    posneg = "same voice"
    if not sample[2]:
        posneg = "Other or generated vocie"
    plot_spec(axes[0], sample[0], title="Original")
    plot_spec(axes[1], sample[1], title=posneg)
    fig.tight_layout()


def plot_explain_siamese_model_all(anchor_sgram, posneg_sgram, anchor_sgram_grad, posneg_sgram_grad):
    plt.figure(figsize=(10, 2))
    plt.subplot(1, 2, 1)
    plt.title("Anchor Sgram")
    plt.imshow(anchor_sgram,  origin="lower", aspect="auto")
    plt.subplot(1, 2, 2)
    plt.title("Anchor Sgram Grad")
    plt.imshow(anchor_sgram_grad.numpy(), cmap=plt.cm.hot,
               origin="lower", aspect="auto")
    plt.figure(figsize=(10, 2))
    plt.subplot(1, 2, 1)
    plt.title("PosNeg Sgram")
    plt.imshow(posneg_sgram,  origin="lower", aspect="auto")
    plt.subplot(1, 2, 2)
    plt.title("PosNeg Sgram Grad")
    plt.imshow(posneg_sgram_grad.numpy(), cmap=plt.cm.hot,
               origin="lower", aspect="auto")
    plt.show()


def plot_explain_siamese_model_image(sgram, sgram_grad, title_sgram, title_sgram_grad):
    plt.figure(figsize=(10, 2))
    plt.subplot(1, 2, 1)
    plt.title(title_sgram)
    plt.imshow(sgram,  origin="lower", aspect="auto")
    plt.subplot(1, 2, 2)
    plt.title(title_sgram_grad)
    plt.imshow(sgram_grad.numpy(), cmap=plt.cm.hot,
               origin="lower", aspect="auto")
    plt.show()
