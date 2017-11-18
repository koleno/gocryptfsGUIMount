from pathlib import Path

from Constants import CONFIG_FILE


class Config:
    """ Reads and saves configuration to a file"""

    def __init__(self):
        self.file = Path(Path.home(), CONFIG_FILE)
        self.mount_folder = ""
        self.cipher_folder = ""

        if not self.file.exists():
            self.file.touch()

        self.__read()

    def __read(self):
        counter = 0

        with self.file.open() as f:
            lines = f.readlines()
            self.cipher_folder = lines[0].rstrip()
            self.mount_folder = lines[1].rstrip()

    def save(self, cipher, mount):
        self.cipher_folder = cipher
        self.mount_folder = mount
        self.file.write_text(cipher + "\n" + mount)
