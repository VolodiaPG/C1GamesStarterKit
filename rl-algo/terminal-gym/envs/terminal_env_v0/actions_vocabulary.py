import enum

class ActionsVocabulary(enum.Enum):
    """
    Describes the vocabulary used to interact
    between the two parts of the algorithm
    """
    Filter = 'a0'
    Encryptor = 'a1'
    Destructor = 'a2'
    Ping = 'a3'
    Emp = 'a4'
    Scrambler = 'a5'
    Bits = 'a6'
    Cores = 'a7'