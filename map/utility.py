def has_three_consecutive(data):
    for i in range(2, len(data)):
        if data[i] == data[i - 1] == data[i - 2]:
            return True
    return False


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

        node, current_path = stack.pop()
        if node not in visited:
            visited.add(node)
            current_path.append(node)
            if all(n in visited for n in node.connected_cores.all()):
                if not has_three_consecutive([n.cable for n in current_path]):
                    paths.append(current_path)

            else:
                for neighbor in node.connected_cores.all():
                    if neighbor not in visited:
                        stack.append((neighbor, current_path.copy()))

    return paths
