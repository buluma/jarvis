import os

# nltk takes ~1s to import, so plugins load it on first use instead of at startup
NLTK_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nltk")


def load_nltk():
    import nltk

    if NLTK_DATA_DIR not in nltk.data.path:
        nltk.data.path.append(NLTK_DATA_DIR)
    return nltk
