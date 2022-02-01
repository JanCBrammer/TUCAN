from operator import gt, lt, eq
from molecule_visualization_utils import print_molecule
from element_props import ELEMENT_PROPS
from collections import deque
import random
import networkx as nx


def graph_from_molfile(filename):
    element_symbols, bonds = _parse_molfile(filename)
    element_colors = [ELEMENT_PROPS[s]["element_color"] for s in element_symbols]
    atomic_numbers = [ELEMENT_PROPS[s]["atomic_number"] for s in element_symbols]
    node_labels = range(len(element_symbols))
    graph = nx.Graph()
    graph.add_nodes_from(node_labels)
    nx.set_node_attributes(graph, dict(zip(node_labels, element_symbols)), "element_symbol")
    nx.set_node_attributes(graph, dict(zip(node_labels, element_colors)), "element_color")
    nx.set_node_attributes(graph, dict(zip(node_labels, atomic_numbers)), "atomic_number")
    nx.set_node_attributes(graph, 0, "partition")
    bonds = [(int(b[0]) - 1, int(b[1]) - 1) for b in bonds]    # make bond-indices zero-based
    graph.add_edges_from(bonds)
    return graph

def _parse_molfile(filename):
    with open(filename) as f:
        lines = [l.rstrip().split(" ") for l in f]
    lines = [[value for value in line if value != ""] for line in lines]
    atom_count = int(lines[5][3])
    bond_count = int(lines[5][4])
    atom_block_offset = 7
    bond_block_offset = atom_block_offset + atom_count + 2
    element_symbols = [l[3] for l in lines[atom_block_offset:atom_block_offset + atom_count]]
    bonds = [(l[4], l[5]) for l in lines[bond_block_offset:bond_block_offset + bond_count]]
    return element_symbols, bonds

def sort_molecule_by_attribute(m, attribute):
    '''Sort atoms lexicographically by attribute.'''
    attr_sequence = [_attribute_sequence(atom, m, attribute) for atom in m]
    idcs = list(range(m.number_of_nodes()))
    attr_with_idcs = [(i, j) for i, j in zip(attr_sequence, idcs)] # [(A, 0), (C, 1), (B, 2)]
    sorted_attr, idcs_sorted_by_attr = zip(*sorted(attr_with_idcs)) # (A, B, C), (0, 2, 1)
    return _relabel_molecule(m, idcs_sorted_by_attr, idcs)

def _attribute_sequence(atom, m, attribute):
    attr_atom = m.nodes[atom][attribute]
    attr_neighbors = sorted([m.nodes[n][attribute] for n in m.neighbors(atom)], reverse=True)
    return [attr_atom] + attr_neighbors

def _relabel_molecule(m, old_labels, new_labels):
    m_relabeled = nx.relabel_nodes(m, dict(zip(old_labels, new_labels)))
    # In the NetworkX Graph datastructure, the relabeled nodes don't occur in
    # increasing order yet. This is why we change the node order now.
    m_sorted = nx.Graph()
    m_sorted.add_nodes_from(sorted(m_relabeled.nodes(data=True)))
    m_sorted.add_edges_from(m_relabeled.edges(data=True))
    return m_sorted

def partition_molecule_by_atomic_numbers(m):
    current_partition = 0
    for i in range(m.number_of_nodes() - 1):
        j = i + 1
        atomic_numbers_i = _attribute_sequence(i, m, "atomic_number")
        atomic_numbers_j = _attribute_sequence(j, m, "atomic_number")
        if (atomic_numbers_i != atomic_numbers_j): current_partition += 1
        m.nodes[j]["partition"] = current_partition
    return m

def partition_molecule_recursively(m, show_steps=False):
    m_sorted = sort_molecule_by_attribute(m, "partition")
    if show_steps:
        print_molecule(m_sorted, "refined partitions")
    current_partitions = list(nx.get_node_attributes(m, "partition").values())
    updated_partitions = [0]
    n_nodes = m.number_of_nodes()
    for i in range(n_nodes - 1):
        j = i + 1
        partitions_i = _attribute_sequence(i, m_sorted, "partition")
        partitions_j = _attribute_sequence(j, m_sorted, "partition")
        current_partition = updated_partitions[-1]
        if (partitions_i != partitions_j):
            current_partition += 1
        updated_partitions.append(current_partition)
    if current_partitions == updated_partitions:
        return m_sorted
    nx.set_node_attributes(m_sorted,
                           dict(zip(range(n_nodes), updated_partitions)),
                           "partition")
    return partition_molecule_recursively(m_sorted, show_steps=show_steps)

def traverse_molecule(m, root_idx, traversal_priorities=[lt, gt, eq], show_traversal_order=False):
    partitions = m.nodes.data("partition")
    lut = _create_partition_lut(m)
    atom_stack = [root_idx]
    canonical_idcs = {}
    nx.set_node_attributes(m, False, "explored")

    while atom_stack:
        a = atom_stack.pop()
        if m.nodes[a]["explored"]:
            continue
        a_canon = lut[partitions[a]].pop()
        canonical_idcs[a] = a_canon
        if show_traversal_order:
            print(f"Current atom index: {a}.\tRe-labeling to {a_canon}.")
        neighbors = list(m.neighbors(a))
        neighbor_traversal_order = []
        for priority in traversal_priorities:
            neighbors_this_priority = [n for n in neighbors
                                       if priority(partitions[a], partitions[n])]
            neighbor_traversal_order.extend(sorted(neighbors_this_priority))

        m.nodes[a]["explored"] = True
        for n in neighbor_traversal_order:
            atom_stack.insert(0, n)

    nx.set_node_attributes(m, False, "explored")
    return canonical_idcs

def _create_partition_lut(m):
    """Look-up-table of atom indices in partitions."""
    partitions = set(sorted([v for k, v in m.nodes.data("partition")]))
    partition_lut = {p:set() for p in partitions}
    for a in m:
        partition_lut[m.nodes[a]["partition"]].add(a)
    partition_lut.update((k, sorted(list(v), reverse=True)) for k, v in partition_lut.items())
    return partition_lut

def canonicalize_molecule(m, root_idx=0):
    m_sorted_by_atomic_numbers = sort_molecule_by_attribute(m, "atomic_number")
    m_partitioned_by_atomic_numbers = partition_molecule_by_atomic_numbers(m_sorted_by_atomic_numbers)
    m_partitioned = partition_molecule_recursively(m_partitioned_by_atomic_numbers, show_steps=False)
    canonical_idcs = traverse_molecule(m_partitioned, root_idx)
    return nx.relabel_nodes(m_partitioned, canonical_idcs, copy=True)

def permute_molecule(m, random_seed=42):
    idcs = m.nodes()
    permuted_idcs = list(range(m.number_of_nodes()))
    random.seed(random_seed)
    random.shuffle(permuted_idcs)
    return _relabel_molecule(m, permuted_idcs, idcs)








def bfs_molecule(m, root_idx):
    """Breadth-first search over atoms.
    Note that NetworkX provides the same algorithm in `dfs_edges()`.
    This (re-)implementation allows for controlling the branching behavior
    during the molecule traversal.
    m: NetworkX graph.
    root_idx: atom at which to start traversal.
    """
    m.nodes[root_idx]["explored"] = True
    atom_queue = deque([root_idx])
    while atom_queue:
        a = atom_queue.popleft()
        for n in m.neighbors(a):
            if m.nodes[n]["explored"]:
                continue
            yield (a, n)
            m.nodes[n]["explored"] = True
            atom_queue.append(n)

def dfs_molecule(m, root_idx):
    """Depth-first search over atoms.
    Note that NetworkX provides the same algorithm in `bfs_edges()`.
    This (re-)implementation allows for controlling the branching behavior
    during the molecule traversal.
    m: NetworkX graph.
    root_idx: atom at which to start traversal.
    """
    m.nodes[root_idx]["explored"] = True
    for n_idx in m.neighbors(root_idx):
        if m.nodes[n_idx]["explored"]:
            continue
        yield (root_idx, n_idx)
        yield from dfs_molecule(m, n_idx)

def edge_dfs_molecule(m, root_idx):
    """Depth-first search over edges.
    Note that NetworkX provides the same algorithm in `edge_dfs ()`.
    This (re-)implementation allows for controlling the branching behavior
    during the molecule traversal.
    m: NetworkX graph.
    root_idx: atom at which to start traversal.
    """
    visited_edges = set()
    visited_nodes = set()
    edges = {}

    nodes = list(m.nbunch_iter(root_idx))
    for start_node in nodes:
        stack = [start_node]
        while stack:
            current_node = stack[-1]
            if current_node not in visited_nodes:
                edges[current_node] = iter(m.edges(current_node))
                visited_nodes.add(current_node)

            try:
                edge = next(edges[current_node])
            except StopIteration:
                # No more edges from the current node.
                stack.pop()
            else:
                edgeid = (frozenset(edge[:2]),) + edge[2:]
                if edgeid not in visited_edges:
                    visited_edges.add(edgeid)
                    # Mark the traversed "to" node as to-be-explored.
                    stack.append(edge[1])
                    yield edge
