
def one_hot_encode_seq(sequence):
    mapping = {
        'A': [1, 0, 0, 0],
        'C': [0, 1, 0, 0],
        'G': [0, 0, 1, 0],
        'T': [0, 0, 0, 1]
    }
    return [mapping.get(base, [0, 0, 0, 0]) for base in sequence.upper()]

def pad_or_truncate(vector_list, max_len, fill_value=None):
    if fill_value is None:
        fill_value = [0, 0, 0, 0] 
        
    if len(vector_list) >= max_len:
        return vector_list[:max_len]
    
    padding_needed = max_len - len(vector_list)
    return vector_list + [fill_value] * padding_needed

def main():
    return ...

