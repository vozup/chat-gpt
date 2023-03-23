import json
import os

import openai
from common.common import parse_conf_file


class Gpt:
    def __init__(self, key_filepath='conf.json'):
        # Gpt instance
        self.op = openai
        self.op.api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") \
            else parse_conf_file(key_filepath, 'OPENAI_API_KEY')
