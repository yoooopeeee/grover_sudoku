from qiskit import IBMQ, QuantumCircuit, ClassicalRegister, QuantumRegister, execute
import numpy as np
import matplotlib.pyplot as plt

template = np.array([4, 0, 2, 0, 0, 1, 0, 4, 1, 0, 4, 0, 0, 4, 0, 2]).reshape(4, 4)
print(template)

print(template[0])
print(template[0][0])


qr = QuantumRegister(30)
cr = ClassicalRegister(30)
qc = QuantumCircuit(qr,cr)

#draws sudoku template
#0 represents an empty cell
#negative value represents an incorrect answer
def draw_matrix(template, template_answer_filled, wrong_indices):
    #compute size of sudoku matrix
    rows = template.shape[0]
    columns = template.shape[1]
    #create vector from sudoku matrix
    flat = template.reshape(1, rows**2)[0]
    #based on the indices of the vector, create a list of empty cell indices
    empty_indices = np.array([np.array([k//4,k%4]) for k in range(rows*columns) if flat[k] == 0])
    #create empty sudoku matrix plot
    fig, ax = plt.subplots(facecolor="w", figsize = (5, 5), dpi = 200)
    #change tick location to match the lines of sudoku matrices
    fig.gca().xaxis.set_major_locator(tick.MultipleLocator(1))
    fig.gca().yaxis.set_major_locator(tick.MultipleLocator(1))
    ax.grid(which='major',color='black',linestyle='-')
    #eliminate ticks
    ax.tick_params(direction = "in", length = 0, colors = "black")
    plt.xlim(0,4)
    plt.ylim(0,4)
    #eliminate ticks
    plt.tick_params(labelbottom=False,
                labelleft=False,
                labelright=False,
                labeltop=False)
    #fill in the corresponding numbers
    for index in [[0,0],[0,1],[0,2],[0,3],[1,0],[1,1],[1,2],[1,3],[2,0],[2,1],[2,2],[2,3],[3,0],[3,1],[3,2],[3,3]]:
        if template_answer_filled[index[0]][index[1]] == 0:
            pass
        elif index in wrong_indices:
            ax.text(index[1] + 0.5, 3 - index[0]+0.5, str(template_answer_filled[index[0]][index[1]]), {'color': 'red', 'fontsize': 24, 'ha': 'center', 'va': 'center'})
        else:
            ax.text(index[1] + 0.5, 3 - index[0]+0.5, str(template[index[0]][index[1]]), {'color': 'black', 'fontsize': 24, 'ha': 'center', 'va': 'center'})
    plt.show()
draw_matrix(template, template, [])

#Input: sudoku matrix, output: list of qubit numbers assigned to each empty cell and
#the list of numbers in the same row, column and qubicle of each empty cell
def nums(template):
    rows = template.shape[0]
    columns = template.shape[1]
    flat = template.reshape(1, rows**2)[0]
    empty_indices = np.array([np.array([k//4,k%4]) for k in range(rows*columns) if flat[k] == 0])
    q_nums = np.array([[k, k+1] for k in range(0, len(empty_indices)*2, 2)])
    num = []
    for k,index in zip(range(len(empty_indices)),empty_indices):
        row = template[index[0]][:]
        column = np.array([template[k][index[1]] for k in range(rows)])
        #if the empty cell belongs to the upper left box
        if index[0] <= 1 and index[1] <= 1:
            box = np.array([template[i[0]][i[1]] for i in [[0,0],[0,1],[1,0],[1,1]]])
        #if the empty cell belongs to the upper right box
        elif index[0] <= 1 and index[1] > 1:
            box = np.array([template[i[0]][i[1]] for i in [[0,2],[0,3],[1,2],[1,3]]])
        #if the empty cell belongs to the lower left box
        elif index[0] > 1 and index[1] <= 1:
            box = np.array([template[i[0]][i[1]] for i in [[2,0],[2,1],[3,0],[3,1]]])
        #if the empty cell belongs to the lower right box
        elif index[0] > 1 and index[1] > 1:
            box =  np.array([template[i[0]][i[1]] for i in [[2,2],[2,3],[3,2],[3,3]]])
        num.append(np.array([row, column, box]).reshape(1, 12)[0])
    return empty_indices, np.array(num)

print(nums(template))


#Input: sudoku matrix,
#Output: list of elements in the same row, column and box of the empty cell in question.
def candidates(template, nums):
    sudoku_size = template.shape[0]
    all_cands = np.arange(1, sudoku_size + 1)
    counts = np.array([np.count_nonzero(nums == all_cands[k]) for k in range(len(all_cands))])
    cand_indices = np.where(counts==0)[0]
    cands = np.array([all_cands[k] for k in cand_indices])
    return cands

print(candidates(template, [0, 4, 0, 2, 2, 0, 4, 0, 1, 0, 0, 4]))

def single_cand_operation(qc, q0, q1, cands):
    if cands[0] == 1:
        pass
    elif cands[0] == 2:
        qc.x(q1)
    elif cands[0] == 3:
        qc.x(q0)
    else:
        qc.x(q0)
        qc.x(q1)

def two_cand_operation(qc, q0, q1, cands):
    product = cands[0]*cands[1]
    #1 + 2
    if product == 2:
        qc.h(q1)
    #1 + 3
    elif product == 3:
        qc.h(q0)
    #1 + 4
    elif product == 4:
        qc.h(q0)
        qc.cx(q0, q1)
    #2 + 3
    elif product == 6:
        qc.x(q1)
        qc.h(q0)
        qc.cx(q0, q1)
    #2 + 4
    elif product == 8:
        qc.x(q1)
        qc.h(q0)
    #3 + 4
    else:
        qc.h(q1)
        qc.x(q0)

def create_initial(qc, q, template):
    draw_matrix(template, template, [])
    empty_indices, num = nums(template)
    cands = np.array([candidates(template, num[k]) for k in range(len(num))])
    for j,k in zip(range(0, len(empty_indices)*2, 2),range(len(cands))):
        if len(cands[k]) == 1:
            single_cand_operation(qc, q[j], q[j+1], cands[k])
        else:
            two_cand_operation(qc, q[j], q[j+1], cands[k])

print(create_initial(qc, qr, template))
