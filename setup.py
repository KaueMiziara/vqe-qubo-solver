from setuptools import setup, find_packages

setup(
    name="qubo_solver",
    version="0.1.0",
    description="Solver for QUBO problems using Qiskit and VQE",
    author="Kaue Miziara",
    author_email="kauemiziara@gmail.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "qiskit",
        "qiskit_optimization",
    ],
)
