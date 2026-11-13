import itertools
import json


COLUMN_NAMES = "xyzpqr"
SIX_INPUTS = ("xyz", "xyp", "xzp", "yzp", "xyq", "xyr")


def project(rows, columns):
    return {tuple(row[index] for index in columns) for row in rows}


def orthogonal_projections(rows, strength):
    width = len(rows[0]) if rows else 2 * strength
    return [
        columns
        for columns in itertools.combinations(range(width), strength)
        if len(project(rows, columns)) == len(rows)
    ]


def gate_rows(alphabet, gate):
    return [tuple(inputs) + tuple(gate(inputs)) for inputs in itertools.product(alphabet, repeat=2)]


def circuit_rows(alphabet, first_gate, middle_gate, last_gate):
    rows = []
    for first, second, third in itertools.product(alphabet, repeat=3):
        upper, lower = first_gate((first, second))
        output_first, inner = middle_gate((upper, third))
        output_second, output_third = last_gate((lower, inner))
        rows.append((first, second, third, output_first, output_second, output_third))
    return rows


def perfect_gate(alphabet, gate):
    return len(orthogonal_projections(gate_rows(alphabet, gate), 2)) == 6


def matrix_gate(matrix, modulus):
    def evaluate(inputs):
        return tuple(sum(entry * value for entry, value in zip(row, inputs)) % modulus for row in matrix)
    return evaluate


def non_affine(alphabet, gate):
    modulus = len(alphabet)
    offset = gate((0, 0))
    first = gate((1, 0))
    second = gate((0, 1))
    return any(
        gate((left, right)) != tuple(
            (base + left * (first_value - base) + right * (second_value - base)) % modulus
            for base, first_value, second_value in zip(offset, first, second)
        )
        for left, right in itertools.product(alphabet, repeat=2)
    )


def partition_projections():
    selected = set()
    for names in SIX_INPUTS:
        columns = tuple(COLUMN_NAMES.index(name) for name in names)
        selected.add(tuple(sorted(columns)))
        selected.add(tuple(index for index in range(6) if index not in columns))
    containing_pair = {
        columns
        for columns in itertools.combinations(range(6), 3)
        if any(set(pair).issubset(columns) for pair in [(0, 1), (2, 3), (4, 5)])
    }
    assert selected == containing_pair and len(selected) == 12
    return sorted(selected)


def check_index_patterns():
    patterns = [
        ("xyz", (("xy", "uv", "xyuv"), ("uz", "pw", "uzpw"), ("vw", "qr", "vwqr")), "pqr"),
        ("xyp", (("xy", "uv", "xyuv"), ("up", "zw", "uzpw"), ("vw", "qr", "vwqr")), "zqr"),
        ("xzp", (("zp", "uw", "uzpw"), ("xu", "yv", "xyuv"), ("vw", "qr", "vwqr")), "yqr"),
        ("yzp", (("zp", "uw", "uzpw"), ("yu", "xv", "xyuv"), ("vw", "qr", "vwqr")), "xqr"),
        ("xyq", (("xy", "uv", "xyuv"), ("vq", "wr", "vwqr"), ("uw", "zp", "uzpw")), "zpr"),
        ("xyr", (("xy", "uv", "xyuv"), ("vr", "wq", "vwqr"), ("uw", "zp", "uzpw")), "zpq"),
    ]
    for inputs, factors, outputs in patterns:
        live = set(inputs)
        summed = []
        used = []
        for domain, codomain, tensor in factors:
            assert set(domain).issubset(live)
            assert set(domain + codomain) == set(tensor)
            assert len(set(domain + codomain)) == 4
            spectator = live - set(domain)
            assert len(spectator) == 1
            assert not spectator.intersection(codomain)
            summed.extend(symbol for symbol in domain if symbol in "uvw")
            used.append(tensor)
            live = spectator | set(codomain)
        assert live == set(outputs)
        assert sorted(summed) == list("uvw")
        assert sorted(used) == sorted(["xyuv", "uzpw", "vwqr"])
        assert set(inputs + outputs) == set(COLUMN_NAMES)
    return len(patterns)


def check_binary():
    alphabet = range(2)
    pairs = list(itertools.product(alphabet, repeat=2))
    gates = []
    for permutation in itertools.permutations(pairs):
        table = dict(zip(pairs, permutation))
        gates.append(table.__getitem__)
    perfect = [perfect_gate(alphabet, gate) for gate in gates]
    twelve = partition_projections()
    global_count = 0
    twelve_count = 0
    circuits = 0
    for first_index, middle_index, last_index in itertools.product(range(24), repeat=3):
        rows = circuit_rows(alphabet, gates[first_index], gates[middle_index], gates[last_index])
        selected = all(len(project(rows, columns)) == 8 for columns in twelve)
        local = perfect[first_index] and perfect[middle_index] and perfect[last_index]
        assert selected == local
        global_perfect = selected and len(orthogonal_projections(rows, 3)) == 20
        global_count += global_perfect
        twelve_count += selected
        circuits += 1
    assert circuits == 13824 and global_count == twelve_count == 0
    return {
        "permutation_gates": len(gates),
        "circuits": circuits,
        "perfect_gates": sum(perfect),
        "perfect_composites": global_count,
        "twelve_projection_composites": twelve_count,
        "six_partition_equivalence": True,
    }


def reverse_rows(alphabet, first_gate, middle_gate, last_gate):
    rows = []
    for first, second, third in itertools.product(alphabet, repeat=3):
        lower, inner = last_gate((second, third))
        upper, output_third = middle_gate((first, inner))
        output_first, output_second = first_gate((upper, lower))
        rows.append((first, second, third, output_first, output_second, output_third))
    return rows


def check_irredundancy():
    alphabet = range(3)
    perfect = matrix_gate(((1, 1), (1, -1)), 3)
    identity = lambda inputs: inputs
    swap = lambda inputs: (inputs[1], inputs[0])
    repeated = matrix_gate(((1, 1), (1, 1)), 3)
    witnesses = [
        (perfect, repeated, perfect),
        (perfect, identity, perfect),
        (identity, perfect, perfect),
        (swap, perfect, perfect),
        (perfect, perfect, identity),
        (perfect, perfect, swap),
    ]
    result = {}
    for omitted, gates in zip(SIX_INPUTS, witnesses):
        rows = circuit_rows(alphabet, *gates)
        sizes = {
            names: [
                len(project(rows, tuple(COLUMN_NAMES.index(symbol) for symbol in names))),
                len(project(rows, tuple(index for index in range(6) if COLUMN_NAMES[index] not in names))),
            ]
            for names in SIX_INPUTS
        }
        assert [names for names, size in sizes.items() if size != [27, 27]] == [omitted]
        assert not all(perfect_gate(alphabet, gate) for gate in gates)
        result[omitted] = sizes
    return result


def check_dual_ternary():
    alphabet = range(3)
    matrices = list(itertools.product(range(3), repeat=4))
    gates = [matrix_gate((entries[:2], entries[2:]), 3) for entries in matrices]
    dual = [
        all(len(project(gate_rows(alphabet, gate), columns)) == 9 for columns in [(0, 1), (2, 3), (0, 3), (1, 2)])
        for gate in gates
    ]
    circuits = 0
    selected_count = 0
    for indices in itertools.product(range(81), repeat=3):
        composite_columns = []
        for basis in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            upper, lower = gates[indices[0]](basis[:2])
            output_first, inner = gates[indices[1]]((upper, basis[2]))
            output_second, output_third = gates[indices[2]]((lower, inner))
            composite_columns.append(basis + (output_first, output_second, output_third))
        selected = all(
            determinant3([[column[index] for column in composite_columns] for index in [COLUMN_NAMES.index(symbol) for symbol in names]]) % 3 != 0
            and determinant3([[column[index] for column in composite_columns] for index in range(6) if COLUMN_NAMES[index] not in names]) % 3 != 0
            for names in ["xyz", "yzp", "xyr"]
        )
        assert selected == all(dual[index] for index in indices)
        circuits += 1
        selected_count += selected
    return {"linear_gates": 81, "circuits": circuits, "dual_gates": sum(dual), "hexagonal_composites": selected_count, "equivalence": True}


def determinant3(matrix):
    return sum(
        (-1 if sum(permutation[left] > permutation[right] for left in range(3) for right in range(left + 1, 3)) % 2 else 1)
        * matrix[0][permutation[0]] * matrix[1][permutation[1]] * matrix[2][permutation[2]]
        for permutation in itertools.permutations(range(3))
    )


def main():
    alphabet = range(5)
    first_gate = matrix_gate(((3, 4), (3, 1)), 5)
    middle_gate = matrix_gate(((4, 1), (1, 3)), 5)
    last_gate = matrix_gate(((3, 1), (3, 4)), 5)
    original = circuit_rows(alphabet, first_gate, middle_gate, last_gate)
    expected_matrix = ((2, 1, 1), (2, 2, 3), (1, 4, 2))
    for row in original:
        assert row[3:] == tuple(sum(entry * value for entry, value in zip(matrix_row, row[:3])) % 5 for matrix_row in expected_matrix)
    assert len(orthogonal_projections(original, 3)) == 20
    assert all(perfect_gate(alphabet, gate) for gate in [first_gate, middle_gate, last_gate])

    def cube(value):
        return value ** 3 % 5

    assert all(cube(cube(value)) == value for value in alphabet)

    def nonlinear_first(inputs):
        return tuple(cube(value) for value in first_gate(inputs))

    def nonlinear_middle(inputs):
        first, second = middle_gate((cube(inputs[0]), inputs[1]))
        return first, cube(second)

    def nonlinear_last(inputs):
        return last_gate((cube(inputs[0]), cube(inputs[1])))

    nonlinear_gates = [nonlinear_first, nonlinear_middle, nonlinear_last]
    nonlinear = circuit_rows(alphabet, *nonlinear_gates)
    assert original == nonlinear
    assert all(non_affine(alphabet, gate) for gate in nonlinear_gates)
    assert all(perfect_gate(alphabet, gate) for gate in nonlinear_gates)
    assert len(orthogonal_projections(nonlinear, 3)) == 20

    def conjugate(gate):
        return lambda inputs: tuple(cube(value) for value in gate(tuple(cube(value) for value in inputs)))

    conjugated_gates = [conjugate(gate) for gate in [first_gate, middle_gate, last_gate]]
    conjugated = circuit_rows(alphabet, *conjugated_gates)
    assert original == reverse_rows(alphabet, first_gate, middle_gate, last_gate)
    assert conjugated == reverse_rows(alphabet, *conjugated_gates)
    assert all(non_affine(alphabet, gate) and perfect_gate(alphabet, gate) for gate in conjugated_gates)
    assert len(orthogonal_projections(conjugated, 3)) == 20
    for row in conjugated:
        base_input = tuple(cube(value) for value in row[:3])
        base_output = next(base[3:] for base in original if base[:3] == base_input)
        assert row[3:] == tuple(cube(value) for value in base_output)

    ternary = range(3)
    equal_gate = matrix_gate(((1, 1), (1, -1)), 3)
    counterexample = circuit_rows(ternary, equal_gate, equal_gate, equal_gate)
    assert perfect_gate(ternary, equal_gate)
    for row in counterexample:
        first, second, third = row[:3]
        assert row[3:] == ((first + second + third) % 3, (2 * first - third) % 3, (-2 * second + third) % 3)
    orthogonal = orthogonal_projections(counterexample, 3)
    assert len(orthogonal) == 16
    witness = [counterexample[0], counterexample[3]]
    assert witness == [(0, 0, 0, 0, 0, 0), (0, 1, 0, 1, 0, 1)]
    assert len(project(witness, (0, 2, 4))) == 1
    assert all(columns in orthogonal for columns in partition_projections())

    boundary = {}
    for size in [0, 1]:
        values = range(size)
        identity = lambda inputs: inputs
        rows = circuit_rows(values, identity, identity, identity)
        assert len(orthogonal_projections(rows, 3)) == 20
        assert perfect_gate(values, identity)
        boundary[str(size)] = {"circuit_rows": len(rows), "gate_perfect": True, "circuit_perfect": True}

    result = {
        "schema_version": 1,
        "arithmetic": "exact integer arithmetic modulo 3 or 5; exact finite-set projections",
        "index_patterns": check_index_patterns(),
        "guaranteed_triples": ["".join(COLUMN_NAMES[index] for index in columns) for columns in partition_projections()],
        "five_symbol_example": {"circuit_rows": 125, "gate_pair_projections": [6, 6, 6], "circuit_triple_projections": 20},
        "nonlinear_relabeling": {"circuit_rows": 125, "non_affine_gates": 3, "gate_pair_projections": [6, 6, 6], "circuit_triple_projections": 20, "same_composite": True},
        "nonlinear_yang_baxter": {"circuit_rows": 125, "non_affine_gates": 3, "gate_pair_projections": [6, 6, 6], "circuit_triple_projections": 20, "opposite_orders_equal": True, "wire_conjugation_formula": True},
        "six_condition_irredundancy": check_irredundancy(),
        "ternary_linear_dual_equivalence": check_dual_ternary(),
        "ternary_counterexample": {
            "circuit_rows": 27,
            "gate_pair_projections": [6, 6, 6],
            "orthogonal_triples": len(orthogonal),
            "failed_triples": ["".join(COLUMN_NAMES[index] for index in columns) for columns in itertools.combinations(range(6), 3) if columns not in orthogonal],
            "collision_projection": "xzq",
            "collision_rows": witness,
        },
        "boundary_alphabets": boundary,
        "binary_exhaustion": check_binary(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
