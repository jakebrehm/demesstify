import re
from datetime import datetime
from typing import List

import pandas as pd

from . import reactions


class Transcript:
    ''''''

    def __init__(self, path: str):
        ''''''

        self._path = path

        self._original = []
        self._cleaned = []
        with open(self._path, 'r') as text:
            for line in text:
                cleaned_line = self._clean_line(line)
                self._cleaned.append(cleaned_line)
                self._original.append(line)

    @property
    def path(self) -> str:
        ''''''
        return self._path
    
    @property
    def original(self) -> List[str]:
        ''''''
        return self._original

    @property
    def cleaned(self) -> List[str]:
        ''''''
        return self._cleaned

    def _clean_line(self, line: str) -> str:
        ''''''

        line = line.replace('“', '"')
        line = line.replace('”', '"')
        line = line.replace('�', '') # iMessage games
        line = line.strip()
        return line
    
    def get(self, original: bool=False) -> List[str]:
        ''''''
        return self._original if original else self._cleaned


class DataParser:
    ''''''

    _LABELS = ['sender', 'phone', 'datetime', 'message', 'reaction']
    _BLOCK_EXPRESSION = r'^(From|Send To) (.*)\((.*)\) at (.*)$'
    # _BLOCK_EXPRESSION = r'^(From|Send To) (.*)\((.*)\) at (.*)\n$'

    def __init__(self, path: str, own_name: str=None, own_phone: str=None):
        ''''''

        self._path = path
        self._own_name = own_name
        self._own_phone = own_phone

        self._transcript = Transcript(self._path)
        self._data = self._parse(self._transcript)
    
    def _parse(self, transcript: Transcript) -> pd.DataFrame:
        ''''''

        all_texts = []
        record = False
        for line in transcript.get():
            if not self._is_valid_message(line):
                record = False
                continue
            if record:
                name = name if direction == 'From' else self._own_name
                phone = phone if direction == 'From' else self._own_phone
                reaction, cleaned = reactions.Reactions.is_reaction(line)
                all_texts.append((name, phone, dt_object, cleaned, reaction))
                record = False
                continue
            if re.match(self._BLOCK_EXPRESSION, line):
                result = re.search(self._BLOCK_EXPRESSION, line)
                direction = result.group(1)
                name = result.group(2)
                phone = result.group(3)
                dt_string = result.group(4)
                dt_object = datetime.strptime(dt_string, r'%b %d, %Y %H:%M:%S')
                record = True
        return self._create_dataframe(all_texts)

    def _is_valid_message(self, line: str) -> bool:
        ''''''

        return line.strip() # Essentially checks if the line is empty

    def _create_dataframe(self, data: List[str]) -> pd.DataFrame:
        ''''''
        
        df = pd.DataFrame(data, columns=self._LABELS)
        return df.set_index(df['datetime'])
    
    def get(self) -> pd.DataFrame:
        ''''''
        return self._data


class iMessages:
    ''''''

    def __init__(self, path: str, own_name: str='Me', own_phone: str='*'):
        ''''''

        self._path = path
        self._own_name = own_name
        self._own_phone = own_phone

        parser = DataParser(self._path, self._own_name, self._own_phone)
        self._data = parser.get()

        self._reactions = reactions.Reactions(messages=self._data)

    def get_all(self, include_reactions: bool=False, as_df: bool=False) -> str:
        ''''''

        if include_reactions:
            data = self.data['message']
        else:
            data = self._remove_reactions(self.data)['message']
        return data if as_df else '\n'.join(data)
    
    def get_sent(self, include_reactions: bool=False, as_df: bool=False) -> str:
        ''''''

        if include_reactions:
            data = self.sent['message']
        else:
            data = self._remove_reactions(self.sent)['message']
        return data if as_df else '\n'.join(data)
    
    def get_received(self, include_reactions: bool=False, as_df: bool=False) -> str:
        ''''''

        if include_reactions:
            data = self.received['message']
        else:
            data = self._remove_reactions(self.received)['message']
        return data if as_df else '\n'.join(data)

    def trim(self, start: str, end: str, replace: bool=True):
        ''''''

        trimmed = self._data.loc[start:end]
        if replace:
            self._data = trimmed
        return trimmed

    def save_all(self, path: str):
        ''''''

        messages = self.get_all()
        with open(path, 'w') as text:
            text.write(messages)

    def _remove_reactions(self, data: pd.DataFrame) -> pd.DataFrame:
        ''''''

        return data[data['reaction'].isnull()]

    @property
    def data(self):
        ''''''
        return self._data

    @property
    def sent(self):
        ''''''
        return self._data[self._data['sender'] == self._own_name]
    
    @property
    def received(self):
        ''''''
        return self._data[self._data['sender'] != self._own_name]