from collections.abc import Iterable

import numpy as np

from .objective import gradient, project_budget

METHODS = ["gd", "momentum", "adam"]


def default_lr(method: str, cov: np.ndarray) -> float:
    if method in ("gd", "momentum"):
        return 1.0 / np.linalg.eigvalsh(cov)[-1]
    if method == "adam":
        return 1e-3
    raise ValueError(f"unknown method {method!r}")


def optimize(
    cov: np.ndarray,
    method: str,
    checkpoints: Iterable[int],
    mu: np.ndarray | None = None,
    lam: float = 0.0,
    lr: float | None = None,
    beta: float = 0.9,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
) -> dict[int, np.ndarray]:
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}")
    checkpoints = sorted(set(checkpoints))
    lr = default_lr(method, cov) if lr is None else lr

    n = cov.shape[0]
    w = np.full(n, 1.0 / n)
    m = np.zeros(n)
    v = np.zeros(n)

    path = {}
    k = 0
    for target in checkpoints:
        while k < target:
            g = project_budget(gradient(w, cov, mu, lam))
            k += 1
            if method == "gd":
                step = g
            elif method == "momentum":
                m = beta * m + g
                step = m
            else:  # adam
                m = beta1 * m + (1 - beta1) * g
                v = beta2 * v + (1 - beta2) * g**2
                m_hat = m / (1 - beta1**k)
                v_hat = v / (1 - beta2**k)
                step = project_budget(m_hat / (np.sqrt(v_hat) + eps))
            w = w - lr * step
        path[target] = w.copy()
    return path
