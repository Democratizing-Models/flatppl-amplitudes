"""Compare full LHCb amplitudes with the pinned source models and JSON checks."""

import json
import subprocess
import unittest
from pathlib import Path

import numpy as np
from test_library import decode

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/fixtures/lhcb.json").read_text())


def model_values(name, points):
    """Return Cartesian amplitude components followed by the intensity."""
    bindings = []
    source = [
        'flatppl_compat = "0.1"',
        f'm = load_module("../examples/lhcb/models/{name}.flatppl")',
    ]
    for i, point in enumerate(points):
        if name.startswith("b2"):
            args = ", ".join(json.dumps(point[j : j + 4]) for j in range(0, 16, 4))
            source.append(f"a{i} = m.amplitude_of_momenta({args})")
            values = f"real(a{i}), imag(a{i})"
            intensity = f"m.intensity_of_momenta({args})"
        else:
            args = ", ".join(map(repr, point))
            source.append(f"a{i} = m.amplitudes_of_sigmas({args})")
            values = ", ".join(
                f"real(a{i}.{a}), imag(a{i}.{a})" for a in CASES[name]["amplitudes"]
            )
            intensity = f"m.intensity_of_sigmas({args})"
        source.append(f"probe{i} = [{values}, {intensity}]")
        bindings.append(f"probe{i}")
    return evaluate("\n".join(source), bindings)


def evaluate(source, bindings):
    run = subprocess.run(
        ["node", str(ROOT / "tests/evaluate.cjs")],
        input=json.dumps({"source": source, "bindings": bindings}),
        capture_output=True,
        text=True,
        check=True,
    )
    return list(map(decode, json.loads(run.stdout)))


class ExampleTests(unittest.TestCase):
    def test_amplitudes_and_intensities(self):
        for name, case in CASES.items():
            with self.subTest(model=name):
                np.testing.assert_allclose(
                    [model_values(name, [point])[0] for point in case["inputs"]],
                    case["values"],
                    rtol=2e-10,
                    atol=2e-10,
                )

    def test_published_lineshapes(self):
        for name, case in CASES.items():
            if not case["lineshapes"]:
                continue
            source = [
                'flatppl_compat = "0.1"',
                f'm = load_module("../examples/lhcb/models/{name}.flatppl")',
            ]
            bindings, expected = [], []
            for i, shape in enumerate(case["lineshapes"]):
                source.append(f"probe{i} = m.{shape['function']}({shape['point']})")
                bindings.append(f"probe{i}")
                expected.append(complex(*shape["value"]))
            with self.subTest(model=name):
                np.testing.assert_allclose(
                    evaluate("\n".join(source), bindings), expected, rtol=2e-12
                )

    def test_coordinate_rates(self):
        for name, case in CASES.items():
            source = [
                'flatppl_compat = "0.1"',
                f'm = load_module("../examples/lhcb/{name}.flatppl")',
            ]
            bindings = []
            for i, point in enumerate(case["coordinate_cases"]):
                fields = ", ".join(f"{k} = {v!r}" for k, v in point.items())
                source.append(f"probe{i} = m.rate_fn(record({fields}))")
                bindings.append(f"probe{i}")
            with self.subTest(model=name):
                np.testing.assert_allclose(
                    evaluate("\n".join(source), bindings),
                    case["rates"],
                    rtol=2e-10,
                    atol=2e-10,
                )


if __name__ == "__main__":
    unittest.main()
