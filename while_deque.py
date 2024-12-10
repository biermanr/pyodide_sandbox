from collections import deque
from line_profiler import profile

def create_large_deque(n):
    return deque(zip(range(n), range(n)))

@profile
def original_loop(pos_mapping, threshold):
    r_idx = None
    while (r_idx is None or r_idx < threshold) and len(pos_mapping) > 0:
        q_idx, r_idx = pos_mapping.popleft()

    return q_idx, r_idx

@profile
def original_loop_no_len(pos_mapping, threshold):
    # can test if the deque is empty directly without len
    r_idx = None
    while (r_idx is None or r_idx < threshold) and pos_mapping:
        q_idx, r_idx = pos_mapping.popleft()

    return q_idx, r_idx

@profile
def clean_while(pos_mapping, threshold):
    while pos_mapping:
        q_idx, r_idx = pos_mapping.popleft()
        if r_idx > threshold:
            break

    return q_idx, r_idx

@profile
def walrus_loop(pos_mapping, threshold):
    # A little awkward with the [1] and the `pass` statement
    # as far as I know, can't assign to a tuple with a walrus
    qr = (None, None)
    while pos_mapping and (qr := pos_mapping.popleft())[1] < threshold:
        pass

    q_idx, r_idx = qr
    return q_idx, r_idx

@profile
def for_loop(pos_mapping, threshold):
    qr = (None, None)
    for _ in range(len(pos_mapping)):
        if (qr := pos_mapping.popleft())[1] >= threshold:
            break

    q_idx, r_idx = qr 
    return q_idx, r_idx

@profile
def no_pop_for(pos_mapping, threshold):
    # NOTE this is not modifying the deque
    # don't have to check length with `for` loop
    for q_idx, r_idx in pos_mapping:
        if r_idx >= threshold:
            break

    return q_idx, r_idx

@profile
def walrus_iter(pos_mapping, threshold):
    # Iterator that does a popleft once per length of the deque except for the last element
    # only returning the (q,r) tuple if the threshold is met
    # This DOES modify the deque
    it = (qr for _ in range(len(pos_mapping)-1) if (qr:=pos_mapping.popleft())[1] >= threshold)

    # Next is called once to get the first value of the iterator that meets the condition
    # (None, None) is returned if the iterator is empty (deque is empty) or condition not met in deque[:-1]
    q_idx, r_idx = next(it, (None, None))

    # If q_idx and r_idx are None and the deque is not empty we'll use return the last element
    # whether or not it passes the threshold.
    # NOTE: Not sure if this is the behavior we want, but it's what the original loop does
    if q_idx is None and r_idx is None and pos_mapping:
        q_idx, r_idx = pos_mapping.popleft()

    return q_idx, r_idx

if __name__ == '__main__':
    n = 50_000_000
    approaches = [original_loop, walrus_loop, for_loop, no_pop_for, original_loop_no_len, walrus_iter, clean_while]

    for approach in approaches:
        dq = create_large_deque(n)
        print(f"Length of deque before {approach.__name__}: {len(dq)}")
        q,r = approach(dq,n)
        print(f"Length of deque after {approach.__name__}: {len(dq)}")
        print(f"q: {q}, r: {r}")
        print("")