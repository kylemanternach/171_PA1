
class vector_clock:
    def __init__(self, num_processes, i):
        self.n = num_processes
        self.V = [0] * num_processes
        self.i = i

    def tick(self):
        self.V[self.i] += 1

    def send(self):
        self.tick()
        return list(self.V)

    def receive(self, other):
        self.V = [max(a, b) for a, b in zip(self.V, other)]
        self.tick()

def leq(v, w):
    return all(a <= b for a, b in zip(v, w))

def happens_before(v, w):
    return leq(v, w) and v != w

def concurrent(v, w):
    return not leq(v, w) and not leq(w, v)

def happens_next(v, w):
    ahead = [b - a for a, b in zip(v, w) if b > a]
    return ahead == [1]
