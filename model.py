from dataclasses import dataclass, asdict
from typing import List, Optional
from PyQt5.QtWidgets import (
    QFileDialog, 
    QMessageBox
)
import json

@dataclass
class Song:
    title: str
    pdf_filename: str
    description_filename: Optional[str] = None

    def title(self):
        title

    def pdf_filename(self):
        pdf_filename

    def description_filename(self):
        description_filename



class Songbook:
    def __init__(self):
        self.songs: List[Song] = []

    def song_count(self):
        return len(self.songs)

    def add_song(self, song: Song, index: Optional[int] = None):
        if index is None:
            self.songs.append(song)
        else:
            self.songs.insert(index, song)

    def remove_song(self, index: int):
        del self.songs[index]

    def move_song(self, old_index: int, new_index: int):
        self.songs.insert(new_index, self.songs.pop(old_index))

    def save(self, filename: str):
        with open(filename, 'w') as f:
            json.dump([asdict(song) for song in self.songs], f, indent=4)

    def load(self, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.songs = [Song(**item) for item in data]

