#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
# Importing standard Qiskit libraries and configuring account
from qiskit import QuantumCircuit, execute, Aer, IBMQ, ClassicalRegister, QuantumRegister
from qiskit.compiler import transpile, assemble
import numpy as np
from qiskit.tools.jupyter import *
from qiskit.visualization import *
# Loading your IBM Q account(s)


# In[2]:


def get_block_index(x, y):
    if x<2 and y<2:
        return 0
    if x<2:
        return 1
    if y<2:
        return 2
    return 3

def get_cands(mat):
    cands = []
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] != 0:
                continue
            # (i, j) に k を置けるか
            tmp = []
            for k in range(4):
                f = True
                for row in range(4):
                    if mat[row][j] == k + 1:
                        f = False
                for col in range(4):
                    if mat[i][col] == k + 1:
                        f = False
                for x in range(4):
                    for y in range(4):
                        if get_block_index(i, j) != get_block_index(x, y):
                            continue
                        if mat[x][y] == k + 1:
                            f = False
                if f:
                    tmp.append(k+1)
            cands.append(tmp)
    return cands


# In[3]:


def single_cand_operation(qc, q0, q1, cands):
    # print(q0, q1)
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
    # print(q0, q1, cands[0], cands[1])
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


# In[4]:


def single_cand_operation_inv(qc, q0, q1, cands): 
    '''identical as noinv'''
    if cands[0] == 1:
        pass
    elif cands[0] == 2:
        qc.x(q1)
    elif cands[0] == 3:
        qc.x(q0)
    else:
        qc.x(q1)
        qc.x(q0)
    
def two_cand_operation_inv(qc, q0, q1, cands):
    product = cands[0]*cands[1]
    #1 + 2
    if product == 2:
        qc.h(q1)
    #1 + 3
    elif product == 3:
        qc.h(q0)
    #1 + 4
    elif product == 4:
        qc.cx(q0, q1)
        qc.h(q0)
    #2 + 3
    elif product == 6:
        qc.cx(q0, q1)
        qc.h(q0)
        qc.x(q1)
    #2 + 4
    elif product == 8:
        qc.h(q0)
        qc.x(q1)
    #3 + 4
    else:
        qc.h(q1)
        qc.x(q0)


# In[5]:


def initialize_blanks(qc, qr, mat):
    cands = get_cands(mat)
    # print(cands)

    for i in range(len(cands)):
        if len(cands[i]) == 1:
            single_cand_operation(qc, qr[2*i], qr[2*i+1], cands[i])
        else:
            two_cand_operation(qc, qr[2*i], qr[2*i+1], cands[i])

def initialize_blanks_inverse(qc, qr, mat):
    cands = get_cands(mat)
    
    for i in range(len(cands)-1, -1, -1):
        if len(cands[i]) == 1:
            single_cand_operation_inv(qc, qr[2*i], qr[2*i+1], cands[i])
        else:
            two_cand_operation_inv(qc, qr[2*i], qr[2*i+1], cands[i])


# In[6]:


# if v1 != v2 (number) then target = 1 else target = 0
def compare_vertex(qc, qr, v1, v2, target):
    qc.x(qr[2*v2])
    qc.x(qr[2*v2+1])
    qc.ccx(qr[2*v1], qr[2*v1+1], target)
    qc.ccx(qr[2*v1+1], qr[2*v2], target)
    qc.ccx(qr[2*v2], qr[2*v2+1], target)
    qc.ccx(qr[2*v1], qr[2*v2+1], target)
    qc.x(qr[2*v2+1])
    qc.x(qr[2*v2])
    #
    qc.x(qr[target])

def compare_vertex_inv(qc, qr, v1, v2, target):
    qc.x(qr[target])
    #
    qc.x(qr[2*v2])
    qc.x(qr[2*v2+1])
    qc.ccx(qr[2*v1], qr[2*v2+1], target)
    qc.ccx(qr[2*v2], qr[2*v2+1], target)
    qc.ccx(qr[2*v1+1], qr[2*v2], target)
    qc.ccx(qr[2*v1], qr[2*v1+1], target)
    qc.x(qr[2*v2+1])
    qc.x(qr[2*v2])

# とりあえず辺埋め込みオラクル
def simple_oracle(qc, qr):
    # vs = [0, 1, 2, 3, 4, 5, 6, 7]
    lst1 = [[0, 1], [2, 3], [4, 5], [6, 7], [2, 6], [0, 4]]
    lst2 = [[1, 5], [3, 7], [0, 2], [1, 3], [4, 6], [5, 7]]
    target = 16
    tmp1 = 30
    tmp2 = 31
    for elm in lst1:
        assert(len(elm)==2)
        compare_vertex(qc, qr, elm[0], elm[1], target)
        target+=1
    qc.mct(qr[16:target], qr[tmp1], qr[22:29], mode='basic')
    for elm in (reversed(lst1)):
        target-=1
        compare_vertex_inv(qc, qr, elm[0], elm[1], target)
        
    for elm in lst2:
        assert(len(elm)==2)
        compare_vertex(qc, qr, elm[0], elm[1], target)
        target+=1
    qc.mct(qr[16:target], qr[tmp2], qr[22:29], mode='basic')
    for elm in (reversed(lst2)):
        target-=1
        compare_vertex_inv(qc, qr, elm[0], elm[1], target)
    
    ##
    dst = 29
    qc.ccx(qr[tmp1], qr[tmp2], qr[dst])
    ##
    
    for elm in lst2:
        assert(len(elm)==2)
        compare_vertex(qc, qr, elm[0], elm[1], target)
        target+=1
    qc.mct(qr[16:target], qr[tmp2], qr[22:29], mode='basic')
    for elm in (reversed(lst2)):
        target-=1
        compare_vertex_inv(qc, qr, elm[0], elm[1], target)
        
    for elm in lst1:
        assert(len(elm)==2)
        compare_vertex(qc, qr, elm[0], elm[1], target)
        target+=1
    qc.mct(qr[16:target], qr[tmp1], qr[22:29], mode='basic')
    for elm in (reversed(lst1)):
        target-=1
        compare_vertex_inv(qc, qr, elm[0], elm[1], target)


# In[7]:


def diffusion(circuit, qr, mat):
    """
    diffusion (inversion about the mean) circuit.
    note that this implementation gives H^{\otimes n} (Id - |0..0><0...0|) H^{\otimes n}
    :param circuit:
    :param qr: QuantumRegister on nodes
    :return:
    """

    # circuit.h(qr)
    initialize_blanks_inverse(circuit, qr[:16], mat)  # 初期状態準備のユニタリ操作のinverse
    circuit.x(qr[:16])

    # apply multi-control CZ
    circuit.h(qr[15])
    # circuit.mct(qr[:-1], qr[-1], anc, mode='basic')
    circuit.mct(qr[:15], qr[15], qr[16:29], mode='basic')  # ancilla使わないver
    circuit.h(qr[15])

    circuit.x(qr[:16])
    # circuit.h(qr)
    initialize_blanks(circuit, qr[:16], mat)


# In[8]:


qr = QuantumRegister(32)
cr = ClassicalRegister(16)
qc = QuantumCircuit(qr, cr)
mat = np.array([4, 0, 2, 0, 0, 1, 0, 4, 1, 0, 4, 0, 0, 4, 0, 2]).reshape(4, 4)
print(mat)
print(get_cands(mat))

def grover(iter):
    initialize_blanks(qc, qr, mat)
    for _ in range(iter):
        simple_oracle(qc, qr)
        print("simple oracle done")
        diffusion(qc, qr, mat)
        print("diffusion done")
    qc.measure(qr[0:16], cr[0:16])
    print("measure done")
    #print("drawing start")
    #qc.draw()


# In[9]:


grover(3)

import json
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller

# Unroll the circuit
pass_ = Unroller(['u3', 'cx'])
pm = PassManager(pass_)
new_circuit = pm.run(qc) 

# obtain gates
gates=new_circuit.count_ops()
print(gates)

cost=gates['u3'] + 10*gates['cx']
print(cost)


# In[10]:


# shots = 8000
shots = 1000
print("shots:", shots)

## local simulator
#backend = Aer.get_backend('qasm_simulator')
## cloud simulator
provider = IBMQ.load_account()
backend = provider.get_backend('ibmq_qasm_simulator')

print("execute start")
job = execute(qc, backend=backend, shots=shots, seed_simulator=12345, backend_options={"fusion_enable":True})
result = job.result()
count = result.get_counts()
print(count)


# In[11]:


print(len(count))


# In[12]:


score_sorted = sorted(count.items(), key=lambda x:x[1], reverse=True)
final_score = score_sorted[0:15]
final_score


# In[13]:


count_sorted = sorted(count.items(), key=lambda x:x[1], reverse=True)

# collect answers with Top 7 probability
ans_list = count_sorted[:12]

# reverse ans_list
ans_reversed = []
for i in ans_list:
    ans_temp=[i[0][::-1],i[1]]
    ans_reversed.append(ans_temp)

# convert each 2 bits into corresponding color. Add node0(0),node3(1),node8(2) and node11(3)
ans_shaped = []
for j in ans_reversed:
    ans_temp=j[0]
    node0 = int(ans_temp[0] + ans_temp[1], 2)
    node1 = int(ans_temp[2] + ans_temp[3], 2)
    node2 = int(ans_temp[4] + ans_temp[5], 2)
    node3 = int(ans_temp[6] + ans_temp[7], 2)
    node4 = int(ans_temp[8] + ans_temp[9], 2)
    node5 = int(ans_temp[10] + ans_temp[11], 2)
    node6 = int(ans_temp[12] + ans_temp[13], 2)
    node7 = int(ans_temp[14] + ans_temp[15], 2)
    nodes_color = str(node0) + str(node1) + str(node2) + str(node3) + str(node4) + str(node5) + str(node6) + str(node7) 
    ans_shaped.append([nodes_color,j[1]])
sorted(ans_shaped)


# In[ ]:




