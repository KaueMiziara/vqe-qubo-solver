from typing import Dict

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import Estimator, StatevectorEstimator
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import LinearEqualityToPenalty, InequalityToEquality

from .ansatz_options import AnsatzOptions


class QuboSolver:
    def __init__(
        self,
        linear_weights: list[float],
        quadratic_weights: list[list[float]],
        n_assets: int,
        problem_name: str,
        constraint_sense: str,
        estimator: Estimator | StatevectorEstimator,
        ansatz_options: AnsatzOptions,
    ) -> None:
        self.__linear_weights = linear_weights
        self.__quadratic_weights = quadratic_weights
        self.__n_assets = n_assets if n_assets else len(linear_weights)

        self.__problem_name = problem_name
        self.__constraint_sense = constraint_sense

        self.__estimator = estimator

        self.__hamilt = self.__create_hamilt()

        self.__ansatz = TwoLocal(
            num_qubits=self.__hamilt.num_qubits,
            rotation_blocks=ansatz_options.rotation_blocks,
            entanglement_blocks=ansatz_options.entanglement_blocks,
            entanglement=ansatz_options.entanglement,
            reps=ansatz_options.reps,
        )

        self.__cost_dict: Dict[str, list[np.ndarray] | int | None] = {
            "prev_vector": None,
            "iters": 0,
            "assets_history": [],
        }

        pass

    def run(self, shots: int, method: str = "COBYLA") -> dict[tuple, int]:
        r = []
        for _ in range(shots):
            x0 = 2 * np.pi * np.random.random(self.__ansatz.num_parameters)
            _ = minimize(
                self.__cost_func,
                x0,
                args=(self.__ansatz, self.__hamilt, self.__estimator, self.__cost_dict),
                method=method,
            )
            r.append(self.__process_results(self.__cost_dict.get("prev_vector")))

        return self.__count_results(r)

    def plot_histogram(self, count_dict: dict) -> None:
        binary_arrays = list(count_dict.keys())
        counts = list(count_dict.values())

        total_count = sum(counts)
        probabilities = [count / total_count for count in counts]

        _, ax = plt.subplots(figsize=(10, 6))

        ax.bar(
            range(len(probabilities)),
            probabilities,
            tick_label=[str(arr) for arr in binary_arrays],
        )

        ax.set_xlabel("Carteiras")
        ax.set_ylabel("Probabilidades")
        ax.set_title("Histograma de Carteiras")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.show()

    def __create_qubo(self) -> QuadraticProgram:
        qubo = QuadraticProgram(self.__problem_name)

        idx = [str(i) for i, _ in enumerate(self.__linear_weights)]

        [qubo.binary_var(i) for i in idx]

        quadratic_weights = {
            (idx[i], idx[j]): self.__quadratic_weights[i][j]
            for i in range(len(self.__quadratic_weights))
            for j in range(i + 1, len(self.__quadratic_weights))
        }

        qubo.minimize(linear=self.__linear_weights, quadratic=quadratic_weights)
        qubo.linear_constraint(
            linear={i: 1 for i in idx},
            sense=self.__constraint_sense,
            rhs=self.__n_assets,
            name="choose_max_N_assets",
        )

        if self.__constraint_sense == "LE" or "GE":
            qubo = InequalityToEquality().convert(qubo)
        qubo = LinearEqualityToPenalty().convert(qubo)

        return qubo

    def __create_hamilt(self) -> SparsePauliOp:
        qubo = self.__create_qubo()
        hamilt, _ = qubo.to_ising()
        return hamilt

    def __process_results(self, results: list[np.ndarray]) -> list[int]:
        smallest_indices = np.argsort(results)[: self.__n_assets]
        binary_array = np.zeros_like(results, dtype=int)

        binary_array[smallest_indices] = 1
        return binary_array.tolist()

    def __count_results(self, results: list[list[float | int]]) -> dict[tuple, int]:
        count_dict = {}
        for arr in results:
            arr_tuple = tuple(arr)
            if arr_tuple in count_dict:
                count_dict[arr_tuple] += 1
            else:
                count_dict[arr_tuple] = 1
        return count_dict

    def __cost_func(self, params, ansatz, hamiltonian, estimator, cost_history_dict):
        """Return estimate of energy from estimator

        Parameters:
            params (ndarray): Array of ansatz parameters
            ansatz (QuantumCircuit): Parameterized ansatz circuit
            hamiltonian (SparsePauliOp): Operator representation of Hamiltonian
            estimator (EstimatorV2): Estimator primitive instance
            cost_history_dict: Dictionary for storing intermediate results

        Returns:
            float: Energy estimate
        """
        pub = (ansatz, [hamiltonian], [params])
        result = estimator.run(pubs=[pub]).result()
        energy = result[0].data.evs[0]

        cost_history_dict["iters"] += 1
        cost_history_dict["prev_vector"] = params
        cost_history_dict["assets_history"].append(params)

        return energy
