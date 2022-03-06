import itertools
import math
import random

from composerstoolkit.core import Sequence, FiniteSequence

class Extinction(Exception): pass

class Evolutionary():

    def __init__(self,
        fitness_func = lambda seq: True,
        transformations = [],
        mutation_threshold = 0.1,
        choose_parents = None,
        debug = True):
        """Generates a musical sequence using an evolutionary-inspired process.
        The process makes use of a pool of weighted candidate functions capable of 
        transforming a givwn musical cell. At each cycle, a weighted random selection 
        process selects a candidate from the pool to transform the base sequence.
        Following this, a user-defined fitness function is used to accept or reject
        the resulting sequence.
        Parents that combine to yeild a successful subject are weighted higher, those
        that yeild an unsuccessful one are weighted down until they reach a weighting
        of zero, and are removed from the pool.
        In addition, a random mutation can occur at each iteration, yeilding a
        new candidate transformer function.
        
        optional args:
        - mutation_threshold - 0.0...1.0 dictates the chance of a random mutation
            occuring at each iteration. This results in a new addition to the pool
        - transformations list of CTTransformer functions, each weighted, eg:
            [(t1, weight), (t2, weight)...]
        - get_offspring (breed?)
        - choose_parents f(parents, weights), should return a 'breeding pair'
            from the pool of candidates:
            ie (parent1, weighting), (parent2, weighting)
        - fitness_func f(seq) -> bool used to evalute 'offspring' (sequences).
            parents of successful offspring will gain a higher weighting
        - debug process should print debug statements (default False)
        """

        self._fitness_func = fitness_func
        self.transformations = transformations
        self.mutation_threshold = mutation_threshold
        self._choose_parents_func = choose_parents
        self.debug = debug

    def _breed(self, p1, p2=None):
        def f(seq):
            if not isinstance(seq.events, list):
                seq.events = list(seq.events)
            x = p1(seq)
            if p2 is None:
                return x
            y = p2(Sequence(x))
            return list(y)
        return f
        
    def _choose_parents(self, parents, weights):
        if self._choose_parents_func is not None:
            return self._choose_parents_func(parents, weights)
        if set(weights) == {0}:
            weights = [0.5 for p in parents]
        choice = random.choices(parents, weights)
        (trans1,w1) = choice[0]
        index = parents.index((trans1,w1))
        remaining_parents = parents[:]
        del remaining_parents[index]
        remaining_weights = weights[:]
        del remaining_weights[index]
        try:
            (trans2,w2) = random.choices(remaining_parents, remaining_weights)[0]
        except IndexError:
            (trans2,w2) = remaining_parents[0]
        return ((trans1,w1), (trans2,w2))
        
    def print_debug(self, *args):
        if self.debug:
            print(args)

    def __call__(self, base_seq: FiniteSequence, n_events=8, debug=False):
        """Model of an evolutionary algorithm.
        """
        result = base_seq
        i = 0
        while i < n_events-1:
            self.print_debug("breeding cycle " + str(i))
            self.print_debug("n breeding types ", len(self.transformations))
            if len(self.transformations) <= 1:
                raise Extinction("There are not enough parents to continue, exiting")
            weights = [y for (x,y) in self.transformations]
            self.print_debug("weights:", weights)
            # a weighted random choice selects the 2 'fittest' parents:
            (trans1,w1), (trans2,w2) = self._choose_parents(self.transformations, weights)
            self.print_debug("will breed:", base_seq)
            child = self._breed(trans1, trans2)
            new_seq = child(base_seq)
            if not isinstance(new_seq, FiniteSequence):
                new_seq = FiniteSequence(new_seq)
            self.print_debug("new_seq", str(result), str(new_seq))
            keep = self._fitness_func(result + new_seq)
            if keep:
                self.print_debug("OK, keeping")
                result = result + new_seq
                #update fitness of both parents
                i1 = self.transformations.index((trans1,w1))
                self.transformations[i1] = (trans1, w1+1)
                i2 = self.transformations.index((trans2,w2))
                self.transformations[i2] = (trans2, w2+1)
                #child inherits avg fitness of two parents
                new_weighting = int((w1 + w2)/2)
                self.transformations.append((child, new_weighting))
                base_seq = new_seq
                i = i+1
                #at the end of each round, possible random mutation in the gene pool...
                randy = random.random()
                if randy >= self.mutation_threshold:
                    # add random parents
                    (trans1,w1) = random.choice(self.transformations)
                    (trans2,w2) = random.choice(self.transformations)
                    if trans1 != trans2:
                        child = self._breed(trans1, trans2)
                    else:
                        child = self._breed(trans1)
                    self.print_debug("added new mutation to breeding pool:", child)
                    new_weighting = int((w1 + w2)/2)
                    self.transformations.append((child, new_weighting))
            else:
                score_down = 0.5
                #parents do not make a good breeding pair, score them down
                i1 = self.transformations.index((trans1,w1))
                if w1-score_down > 0:
                    self.transformations[i1] = (trans1, w1-score_down)
                else:
                    #the parent has partaken in too many bad offspring, so is extinct
                    del self.transformations[i1] #farewell noble beast
                i2 = self.transformations.index((trans2,w2))
                if w2-score_down > 0: 
                    self.transformations[i2] = (trans2, w2-score_down)
                else:
                    del self.transformations[i2]
        return (result, self.transformations)