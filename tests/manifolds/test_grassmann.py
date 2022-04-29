import autograd.numpy as np
from numpy import linalg as la
from numpy import testing as np_testing

from pymanopt.manifolds import Grassmann
from pymanopt.tools import testing
from pymanopt.tools.multi import multieye, multiprod, multisym, multitransp

from .._test import TestCase


class TestSingleGrassmannManifold(TestCase):
    def setUp(self):
        self.m = m = 5
        self.n = n = 2
        self.k = k = 1
        self.man = Grassmann(m, n, k=k)

        self.projection = lambda x, u: u - x @ x.T @ u

    def test_dist(self):
        x = self.man.rand()
        y = self.man.rand()
        np_testing.assert_almost_equal(
            self.man.dist(x, y), self.man.norm(x, self.man.log(x, y))
        )

    def test_ehess2rhess(self):
        # Test this function at some randomly generated point.
        x = self.man.rand()
        u = self.man.random_tangent_vector(x)
        egrad = np.random.randn(self.m, self.n)
        ehess = np.random.randn(self.m, self.n)

        np_testing.assert_allclose(
            testing.ehess2rhess(self.projection)(x, egrad, ehess, u),
            self.man.ehess2rhess(x, egrad, ehess, u),
        )

    def test_retraction(self):
        # Test that the result is on the manifold and that for small
        # tangent vectors it has little effect.
        x = self.man.rand()
        u = self.man.random_tangent_vector(x)

        xretru = self.man.retraction(x, u)

        np_testing.assert_allclose(
            multiprod(multitransp(xretru), xretru), np.eye(self.n), atol=1e-10
        )

        u = u * 1e-6
        xretru = self.man.retraction(x, u)
        np_testing.assert_allclose(xretru, x + u)

    # def test_egrad2rgrad(self):

    # def test_norm(self):

    def test_rand(self):
        # Just make sure that things generated are on the manifold and that
        # if you generate two they are not equal.
        X = self.man.rand()
        np_testing.assert_allclose(
            multiprod(multitransp(X), X), np.eye(self.n), atol=1e-10
        )
        Y = self.man.rand()
        assert la.norm(X - Y) > 1e-6

    # def test_random_tangent_vector(self):

    # def test_transport(self):

    def test_exp_log_inverse(self):
        s = self.man
        x = s.rand()
        y = s.rand()
        u = s.log(x, y)
        z = s.exp(x, u)
        np_testing.assert_almost_equal(0, self.man.dist(y, z), decimal=5)

    def test_log_exp_inverse(self):
        s = self.man
        x = s.rand()
        u = s.random_tangent_vector(x)
        y = s.exp(x, u)
        v = s.log(x, y)
        # Check that the manifold difference between the tangent vectors u and
        # v is 0
        np_testing.assert_almost_equal(0, self.man.norm(x, u - v))

    # def test_pair_mean(self):
    # s = self.man
    # X = s.rand()
    # Y = s.rand()
    # Z = s.pair_mean(X, Y)
    # np_testing.assert_array_almost_equal(s.dist(X, Z), s.dist(Y, Z))


class TestMultiGrassmannManifold(TestCase):
    def setUp(self):
        self.m = m = 5
        self.n = n = 2
        self.k = k = 3
        self.man = Grassmann(m, n, k=k)

        self.projection = lambda x, u: u - x @ x.T @ u

    def test_dim(self):
        assert self.man.dim == self.k * (self.m * self.n - self.n**2)

    def test_typical_dist(self):
        np_testing.assert_almost_equal(
            self.man.typical_dist, np.sqrt(self.n * self.k)
        )

    def test_dist(self):
        x = self.man.rand()
        y = self.man.rand()
        np_testing.assert_almost_equal(
            self.man.dist(x, y), self.man.norm(x, self.man.log(x, y))
        )

    def test_inner(self):
        X = self.man.rand()
        A = self.man.random_tangent_vector(X)
        B = self.man.random_tangent_vector(X)
        np_testing.assert_allclose(np.sum(A * B), self.man.inner(X, A, B))

    def test_projection(self):
        # Construct a random point X on the manifold.
        X = self.man.rand()

        # Construct a vector H in the ambient space.
        H = np.random.randn(self.k, self.m, self.n)

        # Compare the projections.
        Hproj = H - multiprod(X, multiprod(multitransp(X), H))
        np_testing.assert_allclose(Hproj, self.man.projection(X, H))

    def test_retraction(self):
        # Test that the result is on the manifold and that for small
        # tangent vectors it has little effect.
        x = self.man.rand()
        u = self.man.random_tangent_vector(x)

        xretru = self.man.retraction(x, u)

        np_testing.assert_allclose(
            multiprod(multitransp(xretru), xretru),
            multieye(self.k, self.n),
            atol=1e-10,
        )

        u = u * 1e-6
        xretru = self.man.retraction(x, u)
        np_testing.assert_allclose(xretru, x + u)

    # def test_egrad2rgrad(self):

    def test_norm(self):
        x = self.man.rand()
        u = self.man.random_tangent_vector(x)
        np_testing.assert_almost_equal(self.man.norm(x, u), la.norm(u))

    def test_rand(self):
        # Just make sure that things generated are on the manifold and that
        # if you generate two they are not equal.
        X = self.man.rand()
        np_testing.assert_allclose(
            multiprod(multitransp(X), X), multieye(self.k, self.n), atol=1e-10
        )
        Y = self.man.rand()
        assert la.norm(X - Y) > 1e-6

    def test_random_tangent_vector(self):
        # Make sure things generated are in tangent space and if you generate
        # two then they are not equal.
        X = self.man.rand()
        U = self.man.random_tangent_vector(X)
        np_testing.assert_allclose(
            multisym(multiprod(multitransp(X), U)),
            np.zeros((self.k, self.n, self.n)),
            atol=1e-10,
        )
        V = self.man.random_tangent_vector(X)
        assert la.norm(U - V) > 1e-6

    # def test_transport(self):

    def test_exp_log_inverse(self):
        s = self.man
        x = s.rand()
        y = s.rand()
        u = s.log(x, y)
        z = s.exp(x, u)
        np_testing.assert_almost_equal(0, self.man.dist(y, z))

    def test_log_exp_inverse(self):
        s = self.man
        x = s.rand()
        u = s.random_tangent_vector(x)
        y = s.exp(x, u)
        v = s.log(x, y)
        # Check that the manifold difference between the tangent vectors u and
        # v is 0
        np_testing.assert_almost_equal(0, self.man.norm(x, u - v))

    # def test_pair_mean(self):
    # s = self.man
    # X = s.rand()
    # Y = s.rand()
    # Z = s.pair_mean(X, Y)
    # np_testing.assert_array_almost_equal(s.dist(X, Z), s.dist(Y, Z))
