import argparse
import gzip
import io
import json
import os
import xml.etree.ElementTree as ET
import xml.parsers.expat
from datetime import datetime

import xmltodict
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad


class BinaryDecrypter:
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def decrypt_binary_file(self, input_path, output_stream):
        with open(input_path, "rb") as input_file:
            file_buffer = input_file.read()

            t_des = DES.new(self.key, DES.MODE_CBC, self.iv)
            out_buffer = unpad(t_des.decrypt(file_buffer), DES.block_size)

            buffer_size = 4096
            buffer = bytearray(buffer_size)
            with gzip.GzipFile(
                fileobj=io.BytesIO(out_buffer), mode="rb"
            ) as decompression:
                while True:
                    bytes_read = decompression.readinto(buffer)
                    if bytes_read == 0:
                        break
                    output_stream.write(buffer[:bytes_read])


class FileTraverser:
    def __init__(self, base_directory, output_root):
        self.base_directory = base_directory
        self.output_root = output_root
        self.decrypter = BinaryDecrypter(
            key=bytes([48, 239, 114, 71, 66, 242, 4, 50]),
            iv=bytes([14, 166, 220, 137, 219, 237, 220, 79]),
        )

    def save_to_file(self, content, output_file_path):
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(content)

    def is_valid_xml(self, xml_content):
        try:
            ET.fromstring(xml_content)
            return True
        except ET.ParseError:
            return False

    def traverse_decrypt_and_save(self, directory, timestamp):
        content = os.listdir(directory)

        for element in content:
            path = os.path.join(directory, element)

            if os.path.isdir(path):
                self.traverse_decrypt_and_save(path, timestamp)
            else:
                if element.endswith(".bin"):
                    relative_path = os.path.relpath(path, start=self.base_directory)

                    output_folder = os.path.join(self.output_root, f"{timestamp}_dumps")
                    os.makedirs(output_folder, exist_ok=True)

                    with io.BytesIO() as output_stream:
                        self.decrypter.decrypt_binary_file(path, output_stream)
                        output_stream.seek(0)
                        decrypted_content = output_stream.read().decode("utf-8")

                    directory_name = os.path.dirname(relative_path)

                    output_directory = os.path.join(output_folder, directory_name)
                    os.makedirs(output_directory, exist_ok=True)

                    if self.is_valid_xml(decrypted_content):
                        file_extension = ".xml"
                    else:
                        file_extension = ".txt"

                    output_file_path = os.path.join(
                        output_folder, relative_path.replace(".bin", file_extension)
                    )
                    self.save_to_file(decrypted_content, output_file_path)

                    if file_extension == ".xml":
                        try:
                            json_content = json.dumps(
                                xmltodict.parse(decrypted_content), indent=4
                            )

                            json_file_path = os.path.join(
                                output_folder, relative_path.replace(".bin", ".json")
                            )
                            with open(
                                json_file_path, "w", encoding="utf-8"
                            ) as json_file:
                                json_file.write(json_content)
                        except xml.parsers.expat.ExpatError as e:
                            pass


class CommandLineDecrypter:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Decrypts Albion Online files, extracts data, and organizes into readable formats."
        )
        parser.add_argument(
            "-d",
            "--main-game-folder",
            nargs="?",
            default=r"C:\Program Files (x86)\Steam\steamapps\common\Albion Online\game\Albion-Online_Data\StreamingAssets\GameData",
            help="The absolute path of the directory to traverse.",
        )
        parser.add_argument(
            "-o", "--output", help="The destination path for the decrypted files."
        )
        self.args = parser.parse_args()

    def run(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        output_root = self.args.output or os.path.join(os.getcwd(), "dumps")

        file_traverser = FileTraverser(self.args.main_game_folder, output_root)

        file_traverser.traverse_decrypt_and_save(self.args.main_game_folder, timestamp)


if __name__ == "__main__":
    cmd_decrypter = CommandLineDecrypter()
    cmd_decrypter.run()
