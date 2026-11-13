# Resolving Pozsgay–Wanless's factor-perfection question and qubit decomposition conjecture

Haobo Ma (ChronoAI Pte Ltd, Singapore) and Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore).

License: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

## Result

The nonlinear classical question in Pozsgay–Wanless, Quantum 8 (2024), 1339, §5 immediately after equation (5.13), has an affirmative answer: every three-gate classical factorization of an index-one strength-three six-column array has index-one strength-two factor graphs. Six specified balanced permutation flattenings characterize perfect factors. The same implication holds in all six chronological orders, and three hexagonal flattenings characterize ordinary and geometrically dual gates.

For ordinary unitary quantum gates, the six unitary flattenings characterize perfect factors; the forward direction is Pozsgay–Wanless §3.2, Theorems 1–2. For arbitrary complex starting tensors they instead guarantee a decomposition by perfect replacement tensors of the same bond dimension. This excludes every six-qubit absolutely maximally entangled state from the three-vertex triangular network with bond dimension two. Together with the known nonexistence of an eight-qubit AME state (Rains, *Quantum shadow enumerators*, Theorem 14, DOI 10.1109/18.796376; Scott, §III, DOI 10.1103/PhysRevA.69.052330), it settles the §8 qubit decomposition conjecture completely for both constructions studied there, k=6 and k=8. General quantum existence at dimensions three and four and unrestricted circuit gate counts are separate questions.

The replacement proof also shows that a triangle state with maximally mixed dimension-D² node marginals is local-unitarily equivalent, with respect to those three grouped nodes, to three maximally entangled dimension-D pairs (three Bell pairs for D=2).

## Build

The source is self-contained `note.tex`, including its bibliography. Build using Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Alternatively, use a current TeX Live installation:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography uses `thebibliography`, so BibTeX is unnecessary. Required packages are standard: geometry, fontenc, lmodern, amsmath, amssymb, amsthm, booktabs, array, hyperref, and microtype.

## Exact finite checks

Python 3.9 or later, standard library only:

```sh
python3 verify.py > verification-rebuilt.json
python3 -c 'import json; assert json.load(open("verification-rebuilt.json")) == json.load(open("verification.json"))'
```

The checks cover all six pair projections of every displayed perfect gate, all twenty triple projections of the five-symbol composites, their non-affine internal and Yang–Baxter-preserving relabelings, the ternary counterexample, all six irredundancy witnesses, the six matrix-factorization index patterns, and all 13,824 binary permutation-gate circuits. They also check the dual/hexagonal equivalence for all 531,441 triples of linear gates over the three-element field. Empty and singleton alphabets are included. All arithmetic is exact. Finite examples supplement the general written proofs; the quantum theorems have analytic proofs rather than finite-dimensional numerical evidence.

## Formal statement and proof scope

The declaration `D5.S3.Combinatorics.Latin.ClassicalPerfectTensorFactorization.result` in the source below proves the full strength-three-to-strength-two implication, with arbitrary functions on any finite alphabet:

https://github.com/the-omega-institute/trureturing/blob/6715a5bea38a03c80f6c4da6de93fea88798f026/D5/S3/Combinatorics/Latin/ClassicalPerfectTensorFactorization.lean

The six-partition equivalence and its irredundancy, all-order corollary, dual/hexagonal equivalence, symbol relabelings, counterexample, quantum criterion, perfect replacements and six-qubit consequence have written proofs. Eight-qubit nonexistence is the cited consequence of Rains's bound. The underlying formal definitions identify a graph row with its input symbols followed by its output symbols. The linked Lean declaration concerns the classical strength-three-to-strength-two implication; it does not assert the quantum results.

## Contents

- `note.tex`: complete mathematical text and references.
- `metadata.json`: authorship, license, problem identifier, and formal-source link.
- `verify.py`: exact finite checks.
- `verification.json`: deterministic expected check results.
- `README.md`: build commands and mathematical scope.

The separate `note.pdf` is the typeset note.
