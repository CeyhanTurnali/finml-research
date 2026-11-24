import numpy as np
import pytest

from hidden_constraint.objective import closed_form, gradient, project_budget
from hidden_constraint.optimizers import METHODS, optimize


@pytest.fixture
def cov():
    rng = np.random.default_rng(0)
    returns = rng.normal(0, 0.01, size=(500, 5))
    return np.cov(returns, rowvar=False)


def test_closed_form_is_the_bottom(cov):
    w = closed_form(cov)
    assert np.isclose(w.sum(), 1.0)
    assert np.allclose(project_budget(gradient(w, cov)), 0.0, atol=1e-12)


def test_closed_form_with_return_tilt_is_the_bottom(cov):
    mu = np.array([0.05, 0.06, 0.07, 0.08, 0.09])
    w = closed_form(cov, mu, lam=0.05)
    assert np.isclose(w.sum(), 1.0)
    assert np.allclose(project_budget(gradient(w, cov, mu, lam=0.05)), 0.0, atol=1e-12)


@pytest.mark.parametrize("method", METHODS)
def test_budget_is_kept(cov, method):
    path = optimize(cov, method, [0, 1, 10, 100])
    for w in path.values():
        assert np.isclose(w.sum(), 1.0)


@pytest.mark.parametrize("method", ["gd", "momentum"])
def test_converges_to_closed_form(cov, method):
    w = optimize(cov, method, [5000])[5000]
    assert np.allclose(w, closed_form(cov), atol=1e-6)


def test_rank_deficient_cov_raises():
    returns = np.random.default_rng(0).normal(size=(3, 5))
    with pytest.raises(ValueError):
        closed_form(np.cov(returns, rowvar=False))


def test_unknown_method_raises(cov):
    with pytest.raises(ValueError):
        optimize(cov, "sgd", [10])