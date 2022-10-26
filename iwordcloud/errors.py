from typing import List


class ReactionNameError(Exception):
    '''An exception that is thrown when an invalid reaction name is used.'''

    def __init__(self, invalid_name: str, all_names: List[str]):
        '''Inits the ReactionNameError exception.
        
        Args:
            invalid_name:
                Name of the invalid reaction.
            all_names:
                List of all of the valid reaction names.
        '''

        self._invalid_name = invalid_name
        self._all_names = all_names

        error_message = self._construct_message()
        super().__init__(error_message)
    
    def _construct_message(self) -> str:
        '''Constructs and returns the error message.'''

        message = f"'{self._invalid_name}' is an invalid reaction name. "
        message += f"Valid reaction names are {self._all_names}."
        return message