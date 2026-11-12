"""Check compiled LHCb rates, gradients and batching on the selected JAX device."""

import argparse
import json
import os
import statistics
import subprocess
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from enzyme_ad.jax import hlo_call


def timed(function, argument):
    samples = []
    for _ in range(7):
        start = time.perf_counter()
        function(argument).block_until_ready()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modules", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", action="append")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.modules.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        reference = json.loads((root / "tests/fixtures/lhcb.json").read_text())
        if args.model:
            reference = {name: reference[name] for name in args.model}
        cli = os.environ.get("FLATPPL_CLI", "flatppl")
        for name in reference:
            for target in ("cpu", "gpu"):
                for dtype in ("f32", "f64"):
                    path = args.modules / f"{name}-{target}-{dtype}.mlir"
                    start = time.perf_counter()
                    subprocess.run(
                        [
                            cli,
                            "stablehlo",
                            str(root / f"examples/lhcb/{name}.flatppl"),
                            "--target",
                            target,
                            "--dtype",
                            dtype,
                            "-o",
                            str(path),
                        ],
                        check=True,
                        timeout=120,
                    )
                    print(
                        path.name,
                        round(time.perf_counter() - start, 3),
                        "s",
                        flush=True,
                    )
        (args.modules / "expected.json").write_text(json.dumps(reference))
        return
    if args.output is None:
        parser.error("--output is required when executing the modules")
    reference = json.loads((args.modules / "expected.json").read_text())
    if args.model:
        reference = {name: reference[name] for name in args.model}
    jax.config.update("jax_enable_x64", True)
    target = "cpu" if jax.devices()[0].platform == "cpu" else "gpu"
    results = []
    for name, case in reference.items():
        for dtype in ("f32", "f64"):
            source = (args.modules / f"{name}-{target}-{dtype}.mlir").read_text()
            source = source.replace("@logdensity(", "@main(")

            def forward(x, source=source):
                return hlo_call(*x, source=source)[0]

            points = jnp.array(
                [
                    [p[key] for key in case["coordinates"]]
                    for p in case["coordinate_cases"]
                ],
                dtype=jnp.float32 if dtype == "f32" else jnp.float64,
            )
            values = jax.jit(jax.vmap(forward))
            gradients = jax.jit(jax.vmap(jax.grad(forward)))
            start = time.perf_counter()
            actual = np.asarray(values(points))
            value_compile_seconds = time.perf_counter() - start
            np.testing.assert_allclose(
                actual, case["rates"], rtol=2e-3 if dtype == "f32" else 2e-9
            )
            print(
                name,
                dtype,
                "values pass",
                round(value_compile_seconds, 3),
                "s",
                flush=True,
            )
            start = time.perf_counter()
            actual_gradient = np.asarray(gradients(points))
            gradient_compile_seconds = time.perf_counter() - start
            expected = np.asarray(case["rate_gradients"])
            scale = np.maximum(np.max(np.abs(expected), axis=1, keepdims=True), 1e-12)
            error = float(np.max(np.abs(actual_gradient - expected) / scale))
            assert error < (5e-3 if dtype == "f32" else 3e-5), (name, dtype, error)
            result = {
                "model": name,
                "dtype": dtype,
                "value_relative_error": float(
                    np.max(np.abs(actual / case["rates"] - 1))
                ),
                "gradient_scaled_error": error,
                "value_compile_seconds": value_compile_seconds,
                "gradient_compile_seconds": gradient_compile_seconds,
                "batch_size": int(points.shape[0]),
                "value_seconds": timed(values, points),
                "gradient_seconds": timed(gradients, points),
            }
            results.append(result)
            print(json.dumps(result), flush=True)
            args.output.write_text(
                json.dumps(
                    {"device": str(jax.devices()[0]), "cases": results}, indent=2
                )
            )


if __name__ == "__main__":
    main()
