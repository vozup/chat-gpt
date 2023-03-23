import ssl
import urllib.request
import re
from pathlib import Path
import os.path

from PIL import Image

from common.common import get_file_size
from gpt.gpt import Gpt


class ImageSize:
    SIZE256 = "256x256"
    SIZE512 = "512x512"
    SIZE1024 = "1024x1024"


class GptDalle(Gpt):
    def __init__(self):
        super().__init__()

    def images_request(self, prompt: Path, image_size: ImageSize = ImageSize.SIZE512, count=1):
        """
        Creates an image given a prompt or creates a variation of a given image
        :param prompt: may be prompt or filepath to PNG image
        :param count:
        :param image_size:
        :type ImageSize
        n - The number of images to generate. Must be between 1 and 10.
        size - string The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024
        :return: list of links on images, None if error
        """
        if count < 1 or count > 10:
            print("Wrong count of image. Using 2")
            count = 2

        # If prompt is path to file we create a variation of a given image.
        if os.path.exists(Path(prompt)):
            # Check image extension
            if prompt.suffix != '.png':
                print(f"Wrong filetype: {prompt}. Use only .png")
                return None

            # Check file size (must be less then 4Mb)
            file_size = get_file_size(Path(prompt))
            if file_size > 4:
                print(f"Too big file")
                return None

            # Is image squared
            im = Image.open(Path(prompt))
            w, h = im.size
            if w / h != 1:
                print(f"Your image not squared")
                return None

            # Create variation request
            response = None
            print(f"Using Image.create_variation. Prompt: {prompt}")
            try:
                with open(Path(prompt), "rb") as img:
                    response = self.op.Image.create_variation(
                        image=img,
                        n=count,
                        size=image_size
                    )
            except FileNotFoundError:
                print(f"File: {prompt} not found!")
                return None
        # Else create an image from given a prompt
        else:
            print(f"Using Image.create. Prompt: {prompt}")
            response = self.op.Image.create(
                prompt=prompt,
                n=count,
                size=image_size
            )
        return [im['url'] for im in response['data']]

    def request_and_download(self, prompt, image_size: ImageSize = ImageSize.SIZE512,
                             download_dir='download', count=1):
        """
        Creates an image given a prompt or creates a variation of a given image and download them to directory
        :param prompt:
        :param image_size:
        :param download_dir:
        :param count:
        :return: list of paths downloaded files, None if error
        """
        image_links = self.images_request(prompt, image_size, count)
        if not image_links:
            return None

        image_file_paths = []
        if not os.path.exists(download_dir):
            print(f"Creating directory: {download_dir} for downloded files")
            os.makedirs(download_dir)

        for link in image_links:
            filename = img_filename_from_link(link)
            # TODO Ignoring SSL certificates
            ssl._create_default_https_context = ssl._create_unverified_context
            fp, _ = urllib.request.urlretrieve(link, Path(download_dir, filename))
            image_file_paths.append(fp)
            print(f"Downloaded: {Path(fp).absolute()}")

        return image_file_paths


def img_filename_from_link(link, regex=".*\\.(gif|jpe?g|bmp|png)", add_preff='gpt'):
    """
    Parse http link and get downloaded filename
    :param link:
    :param regex:
    :param add_preff: if need prefix for downloaded file from gpt
    :return: filename with ext
    """
    res = re.search(regex, link)
    # Find index of file ext
    last_idx = res.end()
    # Find first index in filename
    first_idx = link[:last_idx].rfind('/')
    # Filename with ext
    return add_preff + link[first_idx + 1:last_idx]
