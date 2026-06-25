import itertools

def generate_kmer_space(k):
    bases = ['A', 'T', 'C', 'G']
    kmers = [''.join(p) for p in itertools.product(bases, repeat=k)]
    return {kmer: i for i, kmer in enumerate(kmers)}
