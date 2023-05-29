import openai
from pathlib import Path
import uuid
import urllib.request
import sys

class OpenAIFile:

    def __init__(self, str):
        self.prompt = str
        self.filename = ""
        self.error = ""
        openai.api_key = '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'
        self.get_file()

    def get_file(self):
        try:
            response = openai.Image.create(prompt=self.prompt, n=1, size="1024x1024")
            image_url = response['data'][0]['url']
            self.filename = sys.path[0] + "/img/" + str(uuid.uuid4()) + ".png"
            page_extractor = urllib.request.build_opener()
            page_extractor.addheaders = [('User-Agent', ' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) '
                                                    'Gecko/20100101 Firefox/12.0')]
            urllib.request.install_opener(page_extractor)
            urllib.request.urlretrieve(image_url, self.filename)
        except Exception as err:
            self.error = err
