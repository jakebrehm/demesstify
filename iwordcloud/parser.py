import re
from datetime import datetime
from typing import List

import pandas as pd

from . import reactions


class Transcript:
    '''Reads the text file and does some preliminary cleaning.
    
    Properties:
        path:
            The path of the text file.
        original:
            The original contents of the text file, split by line.
        cleaned:
            The cleaned contents of the text file, split by line.
    '''

    def __init__(self, path: str):
        '''Inits the Transcript object.'''

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
        '''Returns the path of the text file.'''
        return self._path
    
    @property
    def original(self) -> List[str]:
        '''Returns the original contents of the text file, split by line.'''
        return self._original

    @property
    def cleaned(self) -> List[str]:
        '''Returns the cleaned contents of the text file, split by line.'''
        return self._cleaned

    def get(self, original: bool=False) -> List[str]:
        '''Returns either the original or cleaned data.'''
        return self.original if original else self.cleaned

    def _clean_line(self, line: str) -> str:
        '''Performs some cleaning operations on a string/line.'''

        line = line.replace('“', '"')
        line = line.replace('”', '"')
        line = line.replace('�', '') # iMessage games
        line = line.strip()
        return line


class DataParser:
    '''Parses and cleans a text file containing text messages.'''

    _LABELS = ['sender', 'phone', 'datetime', 'message', 'reaction']
    _BLOCK_EXPRESSION = r'^(From|Send To) (.*)\((.*)\) at (.*)$'

    def __init__(self, path: str, own_name: str=None, own_phone: str=None):
        ''''''

        self._path = path
        self._own_name = own_name
        self._own_phone = own_phone

        self._transcript = Transcript(self._path)
        self._data = self._parse(self._transcript)
    
    def get(self) -> pd.DataFrame:
        '''Returns the message dataframe.'''
        return self._data

    def _parse(self, transcript: Transcript) -> pd.DataFrame:
        '''Parses and cleans the transcript into a dataframe.'''

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
        '''Determines if a line is valid for recording.'''

        return line.strip() # Essentially checks if the line is empty

    def _create_dataframe(self, data: List[str]) -> pd.DataFrame:
        '''Creates a dataframe from a list of strings/lines.'''
        
        df = pd.DataFrame(data, columns=self._LABELS)
        return df.set_index(df['datetime'])
    


class iMessages:
    '''The main object for analyzing iMessage conversations.
    
    Properties:
        data:
            The main dataframe.
        sent:
            The main dataframe filtered by sent messages.
        received:
            The main dataframe filtered by received messages.
        reactions:
            The Reactions object for convenient access to its properties and
            methods.
    '''

    def __init__(self, path: str, own_name: str='Me', own_phone: str='*'):
        '''Inits the iMessages object.'''

        self._path = path
        self._own_name = own_name
        self._own_phone = own_phone

        parser = DataParser(self._path, self._own_name, self._own_phone)
        self._data = parser.get()

        self._reactions = reactions.Reactions(messages=self._data)

    @property
    def data(self) -> pd.DataFrame:
        '''Returns the main dataframe.'''
        return self._data

    @property
    def sent(self) -> pd.DataFrame:
        '''Returns the main dataframe filtered by sent messages.'''
        return self._data[self._data['sender'] == self._own_name]
    
    @property
    def received(self) -> pd.DataFrame:
        '''Returns the main dataframe filtered by received messages.'''
        return self._data[self._data['sender'] != self._own_name]
    
    @property
    def reactions(self) -> reactions.Reactions:
        '''
        Returns the Reactions object for convenient access to its
        properties and methods.
        '''
        return self._reactions

    def get_all(self, include_reactions: bool=False, as_df: bool=False) -> str:
        '''Returns all messages with or without reactions messages.'''

        if include_reactions:
            data = self.data['message']
        else:
            data = self._remove_reactions(self.data)['message']
        return data if as_df else '\n'.join(data)
    
    def get_sent(self, include_reactions: bool=False, as_df: bool=False) -> str:
        '''Returns all sent messages with or without reactions messages.'''

        if include_reactions:
            data = self.sent['message']
        else:
            data = self._remove_reactions(self.sent)['message']
        return data if as_df else '\n'.join(data)
    
    def get_received(self, include_reactions: bool=False, as_df: bool=False) -> str:
        '''Returns all received messages with or without reactions messages.'''

        if include_reactions:
            data = self.received['message']
        else:
            data = self._remove_reactions(self.received)['message']
        return data if as_df else '\n'.join(data)

    def trim(self, start: str, end: str, replace: bool=True) -> pd.DataFrame:
        '''Trims the data to messages sent between a specified time interval.'''

        trimmed = self._data.loc[start:end]
        if replace:
            self._data = trimmed
        return trimmed

    def save_all(self, path: str):
        '''Saves all messages to a text file.'''

        messages = self.get_all()
        with open(path, 'w') as text:
            text.write(messages)

    def _remove_reactions(self, data: pd.DataFrame) -> pd.DataFrame:
        '''Filters out reactions from a message dataframe.'''
        return data[data['reaction'].isnull()]