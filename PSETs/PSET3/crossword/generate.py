import sys
import queue

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for k,v in self.domains.items():
            word_len = k.length
            for word in v.copy():
                if len(word) != word_len:
                    v.remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """        
        is_revised = False
        if self.crossword.overlaps[(x,y)] == None:
            return is_revised

        (i,j) = self.crossword.overlaps[(x,y)]
        x_chars = [(word,word[i]) for word in self.domains[x]]
        y_chars = set([word[j] for word in self.domains[y]])
        for (w,c) in x_chars:
            if c not in y_chars:
                is_revised = True
                self.domains[x].remove(w)
        
        return is_revised

# self.domains
# {
# Variable(0, 1, 'down', 5): {'SEVEN', 'THREE', 'EIGHT'},
# Variable(4, 1, 'across', 4): {'FOUR', 'NINE', 'FIVE'}, 
# Variable(0, 1, 'across', 3): {'TWO', 'ONE', 'TEN', 'SIX'}, 
# Variable(1, 4, 'down', 4): {'FOUR', 'NINE', 'FIVE'}
# }

# self.crossword.overlaps
# {
# (Variable(0, 1, 'down', 5), Variable(4, 1, 'across', 4)): (4, 0), 
# (Variable(0, 1, 'down', 5), Variable(0, 1, 'across', 3)): (0, 0), 
# (Variable(0, 1, 'down', 5), Variable(1, 4, 'down', 4)): None, 
# (Variable(4, 1, 'across', 4), Variable(0, 1, 'down', 5)): (0, 4), 
# (Variable(4, 1, 'across', 4), Variable(0, 1, 'across', 3)): None, 
# (Variable(4, 1, 'across', 4), Variable(1, 4, 'down', 4)): (3, 3), 
# (Variable(0, 1, 'across', 3), Variable(0, 1, 'down', 5)): (0, 0), 
# (Variable(0, 1, 'across', 3), Variable(4, 1, 'across', 4)): None, 
# (Variable(0, 1, 'across', 3), Variable(1, 4, 'down', 4)): None, 
# (Variable(1, 4, 'down', 4), Variable(0, 1, 'down', 5)): None, 
# (Variable(1, 4, 'down', 4), Variable(4, 1, 'across', 4)): (3, 3), 
# (Variable(1, 4, 'down', 4), Variable(0, 1, 'across', 3)): None
# }

    def get_neighbors(self, var):
        variables = list(self.domains.keys())
        var_neighbors = set()
        for x in variables:
            if x != var and self.crossword.overlaps[(var,x)] is not None:
                var_neighbors.add(x) 
        return var_neighbors      

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        q = queue.SimpleQueue()
        variables = list(self.domains.keys())
        # how do I make sure each of the values in assignment is unique? do I do it here?
        if arcs is not None:
            for arc in arcs:
                q.put(arc)
        # I worry about having the x and y's all over the place, I wonder if one can overwrite another in unexpected ways
        else:
            for x in variables:
                for y in self.get_neighbors(x):
                    q.put((x,y))
        while not q.empty():
            (x,y) = q.get()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.get_neighbors(x) - {y}:
                    q.put((z,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # assumes every variable key in assignment actually has some value and that if a variable isn't in assignment, then it hasn't been assigned
        return set(self.domains.keys()) == set(assignment.keys())

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        assignment_words = list(assignment.values())
        if len(set(assignment_words)) != len(assignment_words):
            return False
        for k,v in assignment.items():
            if k.length != len(v):
                return False
        for x in assignment.keys():
            for y in self.get_neighbors(x):
                (i,j) = self.crossword.overlaps[(x,y)]
                if assignment[x][i] != assignment[y][j]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # order from most possibilities to least possibilities
        # when choosing the word, choose the word that rules out the least number of other options
        neighbors = self.get_neighbors(var)
        neighbors = neighbors - set(assignment.keys())
        ans = []
        for word_1 in self.domains[var]:
            cnt = 0
            for nei in neighbors:
                for word_2 in self.domains[nei]:
                    (i,j) = self.crossword.overlaps[(var,nei)]
                    if word_1[i] != word_2[j]:
                        cnt += 1
            ans.append((word_1, cnt))
        ans.sort(key=lambda x: x[1])
        return ans

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        vars = set(self.domains.keys()) - set(assignment.keys())
        return min(map(lambda x: (x, len(self.domains[x])), vars), key=lambda tup: tup[1])[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                assignment[var] = value


                # maintaining arc consistency, when make new assignment, call ac3 with arcs of (y,x) where y are the neighbors of x and both are variables
                #ac-3 are the inferences, yes!!!



                # inferences = self.ac3(assignment)
                # if inferences:
                    # add inferences to assignment
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                del assignment[var] # and inferences from assignment
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
