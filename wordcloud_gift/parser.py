import re
from datetime import datetime

import pandas as pd

import reactions


# class ParsedData:

#     _labels = ['sender', 'phone', 'datetime', 'message', 'reaction']

#     def __init__(self, data):
#         df = pd.DataFrame(self._data, columns=self._labels)
#         self._data = df.set_index(df['datetime'])
    
#     def get_all(self):
#         return self._data

#     # def get_sent(self):
#     #     return self._data

#     # def get_received(self):
#     #     return self._data

#     @property
#     def labels(self):
#         return self._labels


class TranscriptParser:

    _block_expression = r'^(From|Send To) (.*)\((.*)\) at (.*)\n$'

    def __init__(self, path, own_name=None, own_phone=None):
        
        self._path = path
        with open(self._path) as text:
            self._transcript = self._clean_transcript(text.readlines())

        self._own_name = own_name
        self._own_phone = own_phone

        self._reactions = reactions.Reactions()

        self._data = self._parse_transcript(self._transcript)
        self._reactions.update(self._data)
    
    def _clean_transcript(self, text):
        for i, line in enumerate(text):
            line = line.replace('“', '"')
            line = line.replace('”', '"')
            line = line.replace('�', '') # iMessage games
            text[i] = line
        return text

    def _clean_line(self, line):
        return line.strip()

    def _is_valid_message(self, line):
        if not line.strip():
            return False
        return True

    def _parse_reaction_message(self, line):
        for reaction in self._reactions:
            if re.match(fr'^{reaction} \"(.*)\"$', line):
                return reaction
        return None

    def _create_dataframe(self, data):
        labels = ['sender', 'phone', 'datetime', 'message', 'reaction']
        df = pd.DataFrame(data, columns=labels)
        return df.set_index(df['datetime'])

    def _parse_transcript(self, text):
        all_texts = []
        record = False
        for line in text:
            if not self._is_valid_message(line):
                record = False
                continue
            if record:
                cleaned = self._clean_line(line)
                name = name if direction == 'From' else self._own_name
                phone = phone if direction == 'From' else self._own_phone
                # reaction = self._parse_reaction_message(line)
                # reaction = Reactions.is_reaction(line)
                # reaction, cleaned = Reactions.is_reaction(cleaned)
                reaction, cleaned = reactions.Reactions.is_reaction(cleaned)
                # reaction = self._reactions.investigate_line_and_track(line)
                all_texts.append((name, phone, dt_object, cleaned, reaction))
                record = False
                continue
            if re.match(self._block_expression, line):
                result = re.search(self._block_expression, line)
                direction = result.group(1)
                name = result.group(2)
                phone = result.group(3)
                dt_string = result.group(4)
                dt_object = datetime.strptime(dt_string, r'%b %d, %Y %H:%M:%S')
                record = True
        return self._create_dataframe(all_texts)
        # return ParsedData(all_texts)
    
    def trim(self, start, end):
        self._data = self._data.loc[start:end]

    def get_all_messages(self):
        data = self._data[self._data['reaction'].isnull()]['message']
        return '\n'.join(data)
    
    def get_sent_messages(self):
        data = self.sent[self.sent['reaction'].isnull()]['message']
        return '\n'.join(data)

    def get_received_messages(self):
        data = self.received[self.received['reaction'].isnull()]['message']
        return '\n'.join(data)

    def save_all_messages(self, path):
        messages = self.get_all_messages()
        with open(path, 'w') as text:
            text.write(messages)

    @property
    def reactions(self):
        return self._reactions

    @property
    def transcript(self):
        return self._transcript

    @property
    def data(self):
        return self._data
    
    @property
    def sent(self):
        return self._data[self._data['sender'] == self._own_name]
    
    @property
    def received(self):
        return self._data[self._data['sender'] != self._own_name]


if __name__ == '__main__':
    path = r'/Users/jake/Library/CloudStorage/OneDrive-Personal/Python/WordCloud Poster/data/texts.txt'
    output_path = r'/Users/jake/Library/CloudStorage/OneDrive-Personal/Python/WordCloud Poster/data/output.txt'
    parser = TranscriptParser(path, own_name='Me', own_phone='My phone')

    print(parser.reactions.get_count())
    print(parser.reactions.get_count('Loved'))
    # print(parser.reactions.get_count('Loved!'))
    print(parser.reactions.get_messages('Disliked'))
    print(parser.reactions.get_messages())

    for reaction in parser.reactions:
        print(reaction.name)

    # parser.trim('2022-07-02 00:00:00', '2022-07-02 23:59:59')
    # parser.trim('2022-07-02 16:00:00', '2022-07-02 18:00:00')
    # messages = parser.get_all_messages()
    # messages = parser.get_received_messages()
    # parser.save_all_messages(output_path)