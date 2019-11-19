def diffusion(circuit, qr):
    """
    diffusion (inversion about the mean) circuit.
    note that this implementation gives H^{\otimes n} (Id - |0..0><0...0|) H^{\otimes n}
    :param circuit:
    :param qr: QuantumRegister on nodes
    :return:
    """

    # circuit.h(qr)
    initialize_blanks_inverse(circuit, qr)  # 初期状態準備のユニタリ操作のinverse
    circuit.x(qr)

    # apply multi-control CZ
    circuit.h(qr[-1])
    # circuit.mct(qr[:-1], qr[-1], anc, mode='basic')
    circuit.mct(qr[:-1], qr[-1], mode='noancilla')  # ancilla使わないver
    circuit.h(qr[-1])

    circuit.x(qr)
    # circuit.h(qr)
    initialize_blanks(circuit, qr)