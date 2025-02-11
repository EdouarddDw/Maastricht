import sys

def read_scenarios():
    """
    Reads the number of scenarios (n).
    Each scenario line has 6 floats:
       c1, c2, c3, v1, v2, v3
    representing:
       - (c1, c2, c3): capacities of the 3 jugs
       - (v1, v2, v3): initial volumes in each jug
    Returns a list of scenarios: [((c1, c2, c3), (v1, v2, v3)), ...].
    """
    n = int(sys.stdin.readline().strip())
    scenarios = []
    for _ in range(n):  
        line = sys.stdin.readline().strip()
        # Parse 6 floats
        c1, c2, c3, v1, v2, v3 = map(int, line.split())
        scenarios.append(((c1, c2, c3), (v1, v2, v3)))
    return scenarios

def pour(src_volume, dst_volume, dst_capacity):
    """
    Pour water from one jug (src) to another (dst) until:
      - src is empty, OR
      - dst is full
    Returns the new (src_volume, dst_volume).
    """
    space_in_dst = dst_capacity - dst_volume
    amount = min(src_volume, space_in_dst)
    return (src_volume - amount, dst_volume + amount)

def get_next_states(state, capacities):
    """
    Given a current state (v1, v2, v3) and jug capacities (c1, c2, c3),
    return a list of all possible next states by pouring from
    one jug into another.
    """
    (v1, v2, v3) = state
    (c1, c2, c3) = capacities

    volumes = [v1, v2, v3]
    caps    = [c1, c2, c3]
    next_states = []

    # Try pouring from jug i into jug j, for all i != j
    for i in range(3):
        for j in range(3):
            if i != j:
                new_volumes = list(volumes)
                new_volumes[i], new_volumes[j] = pour(volumes[i], volumes[j], caps[j])
                new_state = tuple(new_volumes)
                # Avoid returning the same state if no actual pouring happened
                if new_state != state:
                    next_states.append(new_state)

    return next_states

def dfs(scenario):
    """
    Uses DFS to find all the different reachable volume combinations (states)
    for the given scenario.
    
    scenario = ((c1, c2, c3), (v1, v2, v3))
    """
    (c1, c2, c3) = scenario[0]
    (v1, v2, v3) = scenario[1]

    capacities = (c1, c2, c3)
    initial_state = (v1, v2, v3)

    visited = set()
    stack = [initial_state]

    while stack:
        current_state = stack.pop()
        if current_state not in visited:
            visited.add(current_state)
            # Get all possible next states
            for nxt in get_next_states(current_state, capacities):
                if nxt not in visited:
                    stack.append(nxt)

    return visited

def main():
    scenarios = read_scenarios()

    for i, scenario in enumerate(scenarios, start=1):
        all_reachable_states = dfs(scenario)
        # make it go to the line between each senario to separate them
        if i > 1:
            print()
        for state in all_reachable_states:
            print(*state)

if __name__ == "__main__":
    main()
