"""Numerical checks against SymPy, complex arithmetic, and four-vector geometry."""

import cmath
import json
import math
import subprocess
import unittest
from pathlib import Path

import numpy as np
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan

ROOT = Path(__file__).resolve().parents[1]


def literal(value):
    return json.dumps(value)


def decode(value):
    if isinstance(value, dict) and "shape" in value:
        data = value["data"]
        flat = list(data.values()) if isinstance(data, dict) else data
        return np.asarray([decode(x) for x in flat]).reshape(value["shape"])
    if isinstance(value, dict) and "re" in value:
        return complex(value["re"], value["im"])
    return value


def evaluate(expressions):
    result = []
    for start in range(0, len(expressions), 48):
        run = subprocess.run(
            ["node", str(ROOT / "tests/evaluate.cjs")],
            input=json.dumps(expressions[start : start + 48]),
            text=True,
            capture_output=True,
            check=True,
        )
        result.extend(map(decode, json.loads(run.stdout)))
    return result


def dot(p, q):
    return p[0] * q[0] - np.dot(p[1:], q[1:])


def boost(p, parent, sign=-1):
    beta = sign * parent[1:] / parent[0]
    b2 = np.dot(beta, beta)
    if b2 == 0:
        return p.copy()
    gamma = 1 / math.sqrt(1 - b2)
    matrix = np.eye(4)
    matrix[0, 0] = gamma
    matrix[0, 1:] = gamma * beta
    matrix[1:, 0] = gamma * beta
    matrix[1:, 1:] += (gamma - 1) * np.outer(beta, beta) / b2
    return matrix @ p


def chain_source(chain, i, parent, particles):
    if i == 0:
        return particles[chain]
    return parent if i == chain + 1 else parent - particles[chain]


class LibraryTests(unittest.TestCase):
    def check_cases(self, cases, tolerance=3e-11):
        for actual, (expression, expected) in zip(
            evaluate([c[0] for c in cases]), cases
        ):
            with self.subTest(expression=expression):
                np.testing.assert_allclose(
                    actual, expected, rtol=tolerance, atol=tolerance
                )

    def test_couplings_against_sympy(self):
        cases = []
        for j1 in range(4):
            for j2 in range(4):
                for j in range(abs(j1 - j2), j1 + j2 + 1, 2):
                    for m1 in range(-j1, j1 + 1, 2):
                        for m2 in range(-j2, j2 + 1, 2):
                            m = m1 + m2
                            expected = float(
                                clebsch_gordan(
                                    Rational(j1, 2),
                                    Rational(j2, 2),
                                    Rational(j, 2),
                                    Rational(m1, 2),
                                    Rational(m2, 2),
                                    Rational(m, 2),
                                )
                            )
                            cases.append(
                                (
                                    f"a.clebschgordan_doublearg({j1},{m1},{j2},{m2},{j},{m})",
                                    expected,
                                )
                            )
        cases += [
            ("a.clebschgordan(1,0,1,0,0,0)", -1 / math.sqrt(3)),
            ("a.clebschgordan_doublearg(1,0,1,0,0,0)", 0),
            (
                "a.ls_coupling(two_j=3,two_j1=1,two_j2=2,two_l=2,two_s=1,two_lambda1=1,two_lambda2=0)",
                1 / math.sqrt(6),
            ),
            # J=9/2, L=4, S=1/2 and helicities (1/2,1).
            ("a.ls_coupling(9,1,2,8,1,1,2)", 1 / math.sqrt(3)),
        ]
        self.check_cases(cases)

    def test_wigner_matrices(self):
        for j in (1, 2, 9):
            beta, theta = 0.4, 0.7
            matrices = evaluate(
                [
                    f"a.wignerd_matrix_doublearg({j},{math.cos(x)!r})"
                    for x in (beta, theta, beta + theta)
                ]
            )
            np.testing.assert_allclose(
                matrices[0] @ matrices[1], matrices[2], atol=2e-12
            )
            np.testing.assert_allclose(
                matrices[0] @ matrices[0].T, np.eye(j + 1), atol=2e-12
            )
        c, s = math.cos(0.2), math.sin(0.2)
        self.check_cases(
            [
                ("a.wignerd_matrix_doublearg(1,0.9210609940028851)", [[c, -s], [s, c]]),
                ("a.wignerd_matrix(1,1.0)", np.eye(3)),
            ]
        )

    def test_lineshapes(self):
        cases = []
        for sigma in np.geomspace(5e-5, 8, 100):
            sigma = float(sigma)
            ma, mb = 0.9, 0.2
            rho = cmath.sqrt(1 - (ma + mb) ** 2 / sigma) * cmath.sqrt(
                1 - (ma - mb) ** 2 / sigma
            )
            cases.append((f"a.twobody_phasespace({sigma!r},{ma},{mb})", rho))
            other = cmath.sqrt(1 - 0.5**2 / sigma) * cmath.sqrt(1 - 0.1**2 / sigma)
            denominator = 1.4**2 - sigma - 1j * (0.3 * rho + 0.2 * other)
            cases.append(
                (
                    f"a.resonance_multichannel_breitwigner({sigma!r},1.4,[0.3,0.2],[0.9,0.3],[0.2,0.2],[0,0],[0.0,1.5])",
                    1 / denominator,
                )
            )
        for l in range(8):
            # At z=1 these are the independent integer coefficient sums.
            chi = [1, 2, 13, 277, 12746, 998881, 118394977, 19727003738][l]
            sigma, ma, mb = 4.0, 0.0, 0.0
            cases.append(
                (
                    f"a.resonance_multichannel_breitwigner(4.0,1.4,[0.3],[0.0],[0.0],[{l}],[1.0])",
                    1 / (1.4**2 - sigma - 0.3j / chi),
                )
            )
        cases.append(
            (
                "a.resonance_bugg_breitwigner(0.8,0.824,0.478,0.23397706275638377,0.941060)",
                1
                / (
                    0.824**2
                    - 0.8
                    - 1j
                    * 0.824
                    * 0.478
                    * (0.8 - 0.23397706275638377)
                    / (0.824**2 - 0.23397706275638377)
                    * math.exp(-0.941060 * 0.8)
                ),
            )
        )
        self.check_cases(cases)

    def test_boosts_and_helicity_frames(self):
        rng = np.random.default_rng(234)
        cases = []
        for _ in range(12):
            spatial = rng.normal(size=3)
            parent = np.r_[math.sqrt(2.0**2 + spatial @ spatial), spatial]
            momentum = rng.normal(size=3)
            p = np.r_[math.sqrt(0.4**2 + momentum @ momentum), momentum]
            cases += [
                (f"a.mass_squared({literal(p.tolist())})", 0.16),
                (
                    f"a.boost_to_rest({literal(p.tolist())},{literal(parent.tolist())})",
                    boost(p, parent),
                ),
                (
                    f"a.boost_from_rest({literal(p.tolist())},{literal(parent.tolist())})",
                    boost(p, parent, 1),
                ),
            ]
            for child in (1, 2):
                sign = 3 - 2 * child
                phi = math.atan2(sign * spatial[1], sign * spatial[0])
                theta = math.atan2(np.linalg.norm(spatial[:2]), sign * spatial[2])

                def ry(a):
                    return np.array(
                        [
                            [math.cos(a), 0, math.sin(a)],
                            [0, 1, 0],
                            [-math.sin(a), 0, math.cos(a)],
                        ]
                    )

                def rz(a):
                    return np.array(
                        [
                            [math.cos(a), -math.sin(a), 0],
                            [math.sin(a), math.cos(a), 0],
                            [0, 0, 1],
                        ]
                    )

                rotation = ry(-(child - 1) * math.pi) @ ry(-theta) @ rz(-phi)
                rotated = np.r_[p[0], rotation @ p[1:]]
                frame = boost(rotated, np.r_[parent[0], 0, 0, np.linalg.norm(spatial)])
                cases.append(
                    (
                        f"a.helicity_frame({literal(p.tolist())},{literal(parent.tolist())},{child})",
                        frame,
                    )
                )
                cases.append(
                    (
                        f"a.helicity_angles({literal(p.tolist())},{literal(parent.tolist())},{child}).costheta",
                        frame[3] / np.linalg.norm(frame[1:]),
                    )
                )
                cases.append(
                    (
                        f"a.helicity_angles({literal(p.tolist())},{literal(parent.tolist())},{child}).phi",
                        math.atan2(frame[2], frame[1]),
                    )
                )
        cases += [
            (
                "a.boost_to_rest([2.0,0.1,0.2,0.3],[3.0,0.0,0.0,0.0])",
                [2.0, 0.1, 0.2, 0.3],
            ),
            (
                "a.helicity_frame([2.0,0.1,0.2,0.3],[3.0,0.0,0.0,0.0],1)",
                [2.0, 0.1, 0.2, 0.3],
            ),
        ]
        self.check_cases(cases)

    def test_dalitz_against_rest_frame_angles(self):
        rng = np.random.default_rng(101)
        cases = []
        for massless in (False, True):
            masses = np.array([0.4, 0.6, 0.0 if massless else 0.3])
            M = 3.5
            for _ in range(6):
                pair_mass = rng.uniform(sum(masses[:2]) + 0.1, M - masses[2] - 0.1)

                def q(m, a, b):
                    return math.sqrt(
                        (m * m - (a + b) ** 2) * (m * m - (a - b) ** 2)
                    ) / (2 * m)

                recoil = q(M, pair_mass, masses[2])
                pair = np.array([math.hypot(pair_mass, recoil), 0, 0, recoil])
                third = np.array([math.hypot(masses[2], recoil), 0, 0, -recoil])
                direction = rng.normal(size=3)
                direction *= q(pair_mass, *masses[:2]) / np.linalg.norm(direction)
                first = np.r_[
                    math.sqrt(masses[0] ** 2 + direction @ direction), direction
                ]
                second = np.r_[pair_mass, 0, 0, 0] - first
                particles = [boost(first, pair, 1), boost(second, pair, 1), third]
                parent = np.array([M, 0, 0, 0])
                sigmas = [dot(parent - p, parent - p) for p in particles]
                s, ms = literal(sigmas), literal(masses.tolist())
                for k in range(3):
                    i = (k + 1) % 3
                    frame = parent - particles[k]
                    v1 = boost(particles[i], frame)[1:]
                    v2 = -boost(particles[k], frame)[1:]
                    expected = np.dot(v1, v2) / (
                        np.linalg.norm(v1) * np.linalg.norm(v2)
                    )
                    cases.append(
                        (f"a.dalitz_cos_theta({k + 1},{s},{M},{ms})", expected)
                    )
                    for l in range(3):
                        for i in range(4):
                            if k == l or (i > 0 and masses[i - 1] == 0):
                                expected = 1.0
                            else:
                                rest = parent if i == 0 else particles[i - 1]
                                v1 = boost(chain_source(k, i, parent, particles), rest)[
                                    1:
                                ]
                                v2 = boost(chain_source(l, i, parent, particles), rest)[
                                    1:
                                ]
                                expected = np.dot(v1, v2) / (
                                    np.linalg.norm(v1) * np.linalg.norm(v2)
                                )
                            cases.append(
                                (
                                    f"a.dalitz_cos_zeta({i},{k + 1},{l + 1},{s},{M},{ms})",
                                    expected,
                                )
                            )
        self.check_cases(cases)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(LibraryTests)
    )
    if not result.wasSuccessful():
        raise AssertionError("Library checks failed")
