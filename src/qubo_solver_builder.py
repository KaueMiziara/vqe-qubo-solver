from qiskit.primitives import StatevectorEstimator
from qiskit.primitives.estimator import Estimator

from .ansatz_options import AnsatzOptions
from .qubo_solver import QuboSolver


class QuboSolverBuilder:
    def __init__(
        self,
        linear_weights: list[float],
        quadratic_weights: list[list[float]],
        n_assets: int | None = None,
    ) -> None:
        self.__linear_weights = linear_weights
        self.__quadratic_weights = quadratic_weights
        self.__n_assets = n_assets if n_assets else len(linear_weights)

        self.__problem_name = "QUBO Problem"
        self.__constraint_sense = "EQ"

        self.__estimator = StatevectorEstimator()
        self.__ansatz = AnsatzOptions("ry", "cz", "linear", 0)
        pass

    def build(self) -> QuboSolver:
        return QuboSolver(
            linear_weights=self.__linear_weights,
            quadratic_weights=self.__quadratic_weights,
            n_assets=self.__n_assets,
            problem_name=self.__problem_name,
            constraint_sense=self.__constraint_sense,
            estimator=self.__estimator,
            ansatz_options=self.__ansatz,
        )

    def set_problem(
        self,
        problem_name: str | None,
        constraint_sense: str | None,
    ):
        if problem_name:
            self.__problem_name = problem_name

        if constraint_sense:
            if constraint_sense not in ["LE", "EQ", "GE"]:
                print(f"Error! Invalid sense: {constraint_sense}")
                return

            self.__constraint_sense = constraint_sense

    pass

    def set_estimator(self, estimator: Estimator | StatevectorEstimator | None):
        if estimator:
            self.__estimator = estimator
        pass

    def set_ansatz(
        self,
        rotation_blocks: str | list[str] | None,
        entanglement_blocks: str | list[str] | None,
        entanglement: str | None,
        reps: int | None,
    ):
        if rotation_blocks is None:
            rotation_blocks = "ry"

        if entanglement_blocks is None:
            entanglement_blocks = "cz"

        if entanglement is None:
            entanglement = "linear"

        if entanglement not in [
            "linear",
            "full",
            "reverse_linear",
            "pairwise",
            "circular",
            "sca",
        ]:
            print(f"Error! Invalid entanglement strategy: {entanglement}")

        if reps is None:
            reps = 0

        self.__ansatz = AnsatzOptions(
            rotation_blocks,
            entanglement_blocks,
            entanglement,
            reps,
        )
        pass
