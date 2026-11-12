"""Compile and execute the library on the selected JAX device.

Needs an existing JAX/Enzyme-JAX environment and the two FlatPPL checkouts.
Set FLATPPL_CLI and FLATPPL_JS_DIR when those checkouts are elsewhere.
"""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from enzyme_ad.jax import hlo_call

parser = argparse.ArgumentParser()
parser.add_argument("--modules", type=Path)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
modules = args.modules or Path(tempfile.mkdtemp(prefix="amplitudes-compiled-"))
modules.mkdir(parents=True, exist_ok=True)
jax.config.update("jax_enable_x64", True)


def reference_values(point, source):
    fixed_source = source.replace(
        "x = elementof(interval(-0.75, 0.75))", "x = " + str(point)
    )
    request = {"source": fixed_source, "bindings": ["values"]}
    run = subprocess.run(
        ["node", str(root / "tests/evaluate.cjs")],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        check=True,
    )
    value = json.loads(run.stdout)[0]["data"]
    return np.asarray(list(value.values()) if isinstance(value, dict) else value)


if not args.modules:
    cli = os.environ.get(
        "FLATPPL_CLI", str(root.parent / "flatppl-rust/target/release/flatppl")
    )
    source = (root / "tests/runtime.flatppl").read_text()
    points = [-0.7, 0.0, 0.7]
    expected = []
    derivatives = []
    for point in points:
        expected.append(reference_values(point, source).tolist())
        h = 1e-6
        derivatives.append(
            float(
                np.sum(
                    reference_values(point + h, source)
                    - reference_values(point - h, source)
                )
                / (2 * h)
            )
        )
    (modules / "expected.json").write_text(
        json.dumps({"points": points, "values": expected, "derivatives": derivatives})
    )
    for target in ("cpu", "gpu"):
        for dtype in ("f32", "f64"):
            subprocess.run(
                [
                    cli,
                    "stablehlo",
                    str(root / "tests/runtime.flatppl"),
                    "--target",
                    target,
                    "--dtype",
                    dtype,
                    "-o",
                    str(modules / f"{target}-{dtype}.mlir"),
                ],
                check=True,
            )

reference = json.loads((modules / "expected.json").read_text())
target = "cpu" if jax.devices()[0].platform == "cpu" else "gpu"
results = []
for dtype in ("f32", "f64"):
    text = (
        (modules / f"{target}-{dtype}.mlir")
        .read_text()
        .replace("@logdensity(", "@main(")
    )

    def forward(x, source=text):
        return hlo_call(x, source=source)[0]

    points = jnp.array(
        reference["points"],
        dtype=getattr(jnp, "float32" if dtype == "f32" else "float64"),
    )
    actual = jax.jit(jax.vmap(forward))(points)
    tolerance = 3e-5 if dtype == "f32" else 3e-11
    np.testing.assert_allclose(
        actual, reference["values"], rtol=tolerance, atol=tolerance
    )
    gradient = jax.jit(jax.vmap(jax.grad(lambda x: jnp.sum(forward(x)))))(points)
    gradient_tolerance = 3e-4 if dtype == "f32" else 1e-6
    np.testing.assert_allclose(
        gradient,
        reference["derivatives"],
        rtol=gradient_tolerance,
        atol=gradient_tolerance,
    )
    results.append(
        {
            "dtype": dtype,
            "max_error": float(
                np.max(np.abs(np.asarray(actual) - reference["values"]))
            ),
            "gradient_max_error": float(
                np.max(np.abs(np.asarray(gradient) - reference["derivatives"]))
            ),
        }
    )
args.output.write_text(
    json.dumps(
        {"device": str(jax.devices()[0]), "cases": results, "modules": str(modules)},
        indent=2,
    )
)
print(args.output)
