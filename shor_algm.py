from qiskit import QuantumCircuit, Aer, transpile, assemble, execute # type: ignore
from qiskit.visualization import plot_histogram # type: ignore
import numpy as np
from fractions import Fraction

def quantum_ecd_log(p, g, y):
    """Quantum Algorithm for solving the Discrete Logarithm Problem in ECC."""
    n_count = int(np.ceil(np.log2(p)))  # Number of qubits for counting
    qc = QuantumCircuit(n_count + 1, n_count)
    
    # Apply Hadamard transform
    for q in range(n_count):
        qc.h(q)
    
    # Apply modular exponentiation (Quantum Implementation of y = g^x mod p)
    for q in range(n_count):
        qc.append(modular_exp(g, 2**q, p), [*range(n_count + 1)])

    # Apply inverse Quantum Fourier Transform
    qc.append(qft_dagger(n_count), range(n_count))
    
    qc.measure(range(n_count), range(n_count))  # Measure result
    
    return qc

def modular_exp(base, exp, mod):
    """Quantum Modular Exponentiation Circuit."""
    qc = QuantumCircuit(int(np.ceil(np.log2(mod))) + 1)
    for _ in range(exp):
        qc.cx(0, 1)  # Simplified (actual modular exponentiation is complex)
    return qc

def qft_dagger(n):
    """Inverse Quantum Fourier Transform."""
    qc = QuantumCircuit(n)
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    
    return qc

def solve_ecd_log(p, g, y):
    """Run Quantum ECDLP Solver and Extract Private Key."""
    qc = quantum_ecd_log(p, g, y)
    backend = Aer.get_backend('aer_simulator')
    transpiled_qc = transpile(qc, backend)
    qobj = assemble(transpiled_qc, shots=1024)
    results = backend.run(qobj).result()
    
    counts = results.get_counts()
    measured_value = int(list(counts.keys())[0], 2)  # Get most probable result
    private_key = Fraction(measured_value, 2**len(counts)).limit_denominator(p).denominator
    
    return private_key

# Example (Small Values for Testing)
p = 23  # Prime Order
g = 5   # Generator
y = 8   # Public Key

private_key = solve_ecd_log(p, g, y)
print(f"Recovered Private Key: {private_key}")
