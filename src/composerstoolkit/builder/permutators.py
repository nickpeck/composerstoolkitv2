import itertools

def permutate(starting_list, n_generations=1, return_last_gen_only=False):
    """
    return an unordered set of permutations of starting_list
    if n_generations,then derrive new generations as follows:
        if i is even, divide in two (4 => 2,2),
        else divide unevenly (5 => 3,2)
    if the new generation is {1}, do not bother dividing further
    """
    def _new_generation(l):
        next_gen = []
        for i in l:
            if i <= 1:
                next_gen.append(i)
            elif i % 2 == 0:
                next_gen.append(i/2)
                next_gen.append(i/2)
            else:
                next_gen.append(((i-1)/2) + 1)
                next_gen.append((i-1)/2)
        return [int(i) for i in next_gen]
    results = set()
    for i in range(n_generations):
        perms = list(itertools.permutations(starting_list))
        if return_last_gen_only and i == n_generations-1:
            return list(set(perms))
        results.update(perms)
        if set(perms) == {1}:
            break
        if i < len(range(n_generations)):
            starting_list = _new_generation(starting_list)
    return list(results)