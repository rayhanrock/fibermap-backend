from .models import Connection


def find_core_paths(starting_core):
    """
    Finds all paths from a starting core using backtracking.

    Args:
        starting_core: The core to start the path search from.

    Returns:
        A list of lists, where each sublist represents a path as a sequence of core IDs.
    """
    visited = set()  # Already visited cores
    stack = [(starting_core, [])]  # Stack of unexplored paths
    paths = []
    while stack:
        print('############')
        node, current_path = stack.pop()
        if node not in visited:
            visited.add(node)
            current_path.append(node)
            core_to = [conn.core_to for conn in Connection.objects.filter(core_from=node)]
            if all(n in visited for n in core_to):
                paths.append(current_path)

            else:
                for neighbor in core_to:
                    if neighbor not in visited:
                        stack.append((neighbor, current_path.copy()))

    result = []
    for path in paths:
        if path[0].cable == path[1].cable:

            while path[-1].cable is None:
                path.pop()
            result.append(path[0])
            for i in range(1, len(path)):
                if result[-1].marker == path[i].marker:
                    result.pop()
                    result.append(path[i])
                else:
                    result.append(path[i])
            break
    return result
