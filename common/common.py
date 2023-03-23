import json
import os
from pathlib import Path


# TODO check existing file conf.json (create if not found)
def parse_conf_file(key_filepath='conf.json', key=None):
    """
    Get api key from json file with {key: "OPENAI_API_KEY" data: "your_api_key"
    :param key_filepath:
    :param key:
    :return:
    """
    try:
        with open(Path(key_filepath), 'r') as f:
            data = json.load(f)
        if not key:
            return data
        return data[key]
    except FileExistsError:
        print(f"File: {key_filepath} dont find.")
        print(f"You need place conf file into root app directory. The file must be named: conf.json")
        return None
    # TODO work on exception
    except KeyError:
        error_text = ""
        if key.lower().find('telegram') != -1:
            error_text += "Maybe you meant TELEGRAM_TOKEN"
        elif key.lower().find('openai') != -1:
            error_text += "Maybe you meant OPENAI_API_KEY"
        raise Exception(error_text)


def get_file_size(file_path, return_size_in='mb'):
    """
    Get file size
    :param file_path: path to file
    :param return_size_in: output format:
    'mb' - mbytes
    'kb - kbytes
    'b' - bytes
    :return: None if error; result in float
    """

    if not os.path.isfile(file_path):
        print(f"{file_path} is not a file")
        return None
    try:
        file_size = os.path.getsize(file_path)
        if return_size_in == 'mb':
            file_size = file_size / (1024 * 1024)
            return file_size
        if return_size_in == 'kb':
            return file_size / 1024
        return file_size
    except FileNotFoundError:
        print(f"File {Path(file_path).name} not found")
        return None
