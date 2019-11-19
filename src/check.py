import numpy as np
import math
import matplotlib.ticker as tick

template_answer_filled = np.array([[4, 1, 2, 1], [2, 1, 3, 4], [1, 2, 4, 3], [3, 4, 1, 2]])

template = np.array([[4, 0, 2, 0], [0, 1, 0, 4], [1, 0, 4, 0], [0, 4, 0, 2]])

correct_template = np.array([[4, 3, 2, 1], [2, 1, 3, 4], [1, 2, 4, 3], [3, 4, 1, 2]])

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

#Determines the values in the box in which the cell is contained
def determine_box(template, row, column):
    if row <= 1 and column <= 1:
        box = np.array([template[i[0]][i[1]] for i in [[0,0],[0,1],[1,0],[1,1]]])
        #if the empty cell belongs to the upper right box
    elif row <= 1 and column > 1:
        box = np.array([template[i[0]][i[1]] for i in [[0,2],[0,3],[1,2],[1,3]]])
        #if the empty cell belongs to the lower left box
    elif row > 1 and column <= 1:
        box = np.array([template[i[0]][i[1]] for i in [[2,0],[2,1],[3,0],[3,1]]])
        #if the empty cell belongs to the lower right box
    elif row > 1 and column > 1:
        box =  np.array([template[i[0]][i[1]] for i in [[2,2],[2,3],[3,2],[3,3]]])
    return box

#fill in the blanks
def fill(template, sequence):
    #the number of rows of the sudoku matrix
    rows = template_answer_filled.shape[0]
    #the number of columns of the sudoku matrix
    columns = template_answer_filled.shape[1]
    #sudoku matrix converted into a vector
    flat = template.reshape(1, rows**2)[0]
    #array containing the indices of the empty cells of the initial sudoku matrix
    empty_rows = np.array([k//4 for k in range(rows*columns) if flat[k] == 0])
    empty_cols = np.array([k%4 for k in range(rows*columns) if flat[k] == 0])
    #fill in
    for i, j, k in zip(empty_rows,empty_cols, range(len(sequence))):
        template[i][j] = sequence[k]
    return template

sequence = [3,1,2,3,2,3,3,1]
print(fill(template, sequence))

#checks that a given sudoku matrix has the correct sum for each row, column and box.
#returns the template
def check(template, template_answer_filled):
    #the number of rows of the sudoku matrix
    rows = template_answer_filled.shape[0]
    #the number of columns of the sudoku matrix
    columns = template_answer_filled.shape[1]
    #the correct sum of each row, column or box
    correct_sum = np.sum([k for k in range(1, rows+1)])
    #sudoku matrix converted into a vector
    flat = template.reshape(1, rows**2)[0]
    #array containing the indices of the empty cells of the initial sudoku matrix
    empty_rows = np.array([k//4 for k in range(rows*columns) if flat[k] == 0])
    empty_cols = np.array([k%4 for k in range(rows*columns) if flat[k] == 0])
    #list to be filled with indices of cells containing wrong answers
    wrong_indices = []
    #checks each element in terms of the sum of the row, column and box.
    for i, j in zip(empty_rows, empty_cols):
        row = np.sum(template_answer_filled[i][:])
        column = np.sum([template_answer_filled[k][j] for k in range(rows)])
        box = np.sum(determine_box(template_answer_filled, i, j))
        if row == correct_sum and column == correct_sum and box == correct_sum:
            pass
        else:
            wrong_indices.append([i,j])
    return wrong_indices

wrong_indices = check(template, template_answer_filled)
print(wrong_indices)

draw_matrix(template, template_answer_filled, wrong_indices)
