import numpy as np


def makeMatrixFullRank(A):
    ''' Esta função recebe uma matriz, que pode ser em numpy,
        e retorna dois argumentos:
          - A matriz com linhas eliminadas
          - Uma lista indicando quais linhas foram eliminadas.
    '''
    if np.linalg.matrix_rank(A) == A.shape[0]:
        return A, []
    row = 1
    rowsEliminated = []
    counter = 0
    while 1:
        counter += 1
        B = A[0:(row+1), :]
        C = np.linalg.qr(B.T)[1]
        C[np.isclose(C, 0)] = 0
        if not np.any(C[row, :]):
            rowsEliminated.append(counter)
            A = np.delete(A, (row), axis=0)
        else:
            row += 1
        if row >= A.shape[0]:
            break
    return A, rowsEliminated


def pivot_element(A: np.ndarray, pivot_row: int, pivot_col: int):
    """Realiza o pivoteamento em torno de um elemento de uma matriz.

    Parâmetros
    ----------
    A : numpy.ndarray
        Matriz a ser modificada (geralmente em forma reduzida de linhas ou tableau Simplex).
    pivot_row : int
        Índice da linha do elemento pivô.
    pivot_col : int
        Índice da coluna do elemento pivô.

    Observações
    -----------
    - A função espera que o elemento pivô seja não-nulo; 
    - Altera a matriz de entrada in-place.
    """

    assert A[pivot_row, pivot_col] != 0, "Elemento pivô não pode ser zero."

    for i in range(0, A.shape[0]):
        if i != pivot_row:
            A[i, :] = A[i, :] - A[pivot_row, :] * \
                (A[i, pivot_col] / A[pivot_row, pivot_col])

    A[pivot_row, :] = A[pivot_row, :] / A[pivot_row, pivot_col]

    # Corrige precisão de divisão para evitar valores muito pequenos que deveriam ser zero
    A[np.isclose(A, 0)] = 0

    for i in range(0, A.shape[0]):
        if i == pivot_row:
            assert A[i,
                     pivot_col] == 1, f"Após pivoteamento, o elemento pivô deve ser 1. Encontrado {A[i, pivot_col]} na linha {i}."
        else:
            assert A[i,
                     pivot_col] == 0, f"Após pivoteamento, elementos na coluna do pivô devem ser zero. Encontrado {A[i, pivot_col]} na linha {i}."
