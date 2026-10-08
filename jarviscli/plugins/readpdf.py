# importing the modules
from pypdf import PdfReader
from plugin import plugin

"""Read PDF text through Jarvis's normal output and speech interface."""


def extract_page_text(filename):
    """Return text for each page in a PDF, preserving empty pages."""
    reader = PdfReader(filename)
    try:
        return [page.extract_text() or "" for page in reader.pages]
    finally:
        reader.close()


@plugin('readpdf')
class readpdfjarvis():

    def __init__(self):
        self.path = None

    def __call__(self, jarvis, s):
        self.read_pdf(jarvis)

    def read_pdf(self, jarvis):
        filename = jarvis.input("Enter your file path with '/' separations:")
        for page_number, page_content in enumerate(extract_page_text(filename), start=1):
            jarvis.say("Page No: {}".format(page_number))
            jarvis.say(page_content)
