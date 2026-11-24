import numpy as np


def variance(w: np.ndarray, cov: np.ndarray) -> float:

    return float(w.T @ cov @ w)


def gradient(w: np.ndarray, cov: np.ndarray, mu: np.ndarray | None = None, lam: float = 0.0):
    g = cov @ w
    if lam:
        g = g - lam * mu
    return g


def project_budget(g: np.ndarray) -> np.ndarray:
    return g - g.mean()


def closed_form(cov: np.ndarray, mu: np.ndarray | None = None, lam: float = 0.0):
    n = cov.shape[0]
    if np.linalg.matrix_rank(cov) < n:
        raise ValueError(
            f"covariance is rank-deficient (rank {np.linalg.matrix_rank(cov)} < {n} assets); "
            "the exact optimum is not unique"
        )
    inv_ones = np.linalg.solve(cov, np.ones(n))
    w_gmv = inv_ones / inv_ones.sum()
    if not lam:
        return w_gmv
    inv_mu = np.linalg.solve(cov, mu)
    tilt = inv_mu - inv_mu.sum() * w_gmv
    return w_gmv + lam * tilt
