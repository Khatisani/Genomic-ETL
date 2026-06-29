import itertools
import numpy as np 

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

def run_transformation(input_path, output_path, kmer_size):
    kmer_dict = generate_kmer_space(kmer_size)
    feature_matrix = []
    
    with open(input_path, 'r') as infile:
        while True:
            header = infile.readline().strip()
            if not header:
                break
                
            sequence = infile.readline().strip()
            
            frequencies = sequence_to_kmer_frequencies(sequence, kmer_dict, kmer_size)
            feature_matrix.append(frequencies)
            
    np_matrix = np.array(feature_matrix, dtype=np.float32)
    np.save(output_path, np_matrix)
    
    print(f"Transformation Profile:")
    print(f"   - Engineered Feature Space Matrix Shape: {np_matrix.shape}")
    print(f"   - Total Extracted Feature Dimension Size: {np_matrix.shape[1]} columns")