
def one_hot_encode_seq(sequence):
    mapping = {
        'A': [1, 0, 0, 0],
        'C': [0, 1, 0, 0],
        'G': [0, 0, 1, 0],
        'T': [0, 0, 0, 1]
    }
    return [mapping.get(base, [0, 0, 0, 0]) for base in sequence.upper()]

def main():
    return ...

