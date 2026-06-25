import itertools

def generate_kmer_space(k):
    bases = ['A', 'T', 'C', 'G']
    kmers = [''.join(p) for p in itertools.product(bases, repeat=k)]
    return {kmer: i for i, kmer in enumerate(kmers)}

def sequence_to_kmer_frequencies(sequence, kmer_dict, k):
    frequencies = [0.0] * len(kmer_dict)
    num_kmers = len(sequence) - k + 1
    
    if num_kmers <= 0:
        return frequencies
        
    for i in range(num_kmers):
        kmer = sequence[i:i+k]
        if kmer in kmer_dict:
            frequencies[kmer_dict[kmer]] += 1.0
            
    return [count / num_kmers for count in frequencies]
