import base64
import os
UPLOAD_DIRECTORY = 'data/data_for_prediction'
def save_target_func(content):
    target_file_path = os.path.join(UPLOAD_DIRECTORY, "new_target.jpg")

    if content is not None:
        data = content.encode("utf8").split(b";base64,")[1]
        with open(target_file_path, "wb") as fp:
            fp.write(base64.decodebytes(data))