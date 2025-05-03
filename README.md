## 🔧 pyModRev: A Python Tool for Model Revision in Boolean Networks

**pyModRev** is a Python-based reimplementation of [ModRev](https://github.com/cristianecosta/modrev), a tool for automated **consistency checking** and **repair** of Boolean network models using **Answer Set Programming (ASP)**. Given a Boolean model and a set of experimental observations (steady-state or time-series), pyModRev determines whether the model explains the data. If inconsistencies are found, it identifies **minimal repair operations** to fix the model.

Built on top of the [Clingo](https://potassco.org/clingo/) ASP solver and the [`pyfunctionhood`](https://github.com/ptgm/pyfunctionhood) library, pyModRev brings modern usability and extensibility to the model revision process by offering:

* ✅ **Full parity with ModRev's core logic**, using the same ASP encodings
* 🧩 **Modular architecture** with pluggable update policies (synchronous, asynchronous, complete, steady-state)
* 🐍 **Pure Python interface**, ideal for integration with scientific workflows
* 📁 **In-memory model and observation management**, enabling multiple consistency checks without reloading
* ⚙️ **Command-line interface** for batch processing and reproducibility

---

### 🚀 Getting Started

To run pyModRev:

```bash
$ python3 main.py -m <model_file.lp> -obs <observation.lp> <updater> [options]
```