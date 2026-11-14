"""Check the live model's posterior against independent complex arithmetic."""

import cmath
import json
import math
import subprocess
from pathlib import Path


def score(pole):
    total = -math.log(0.03)
    for mass, observed in zip([1.36, 1.38, 1.40, 1.42, 1.44], [19, 35, 91, 160, 42]):
        s = mass * mass
        channels = sum(
            cmath.sqrt(1 - (a + b) ** 2 / s) * cmath.sqrt(1 - (a - b) ** 2 / s)
            for a, b in [(0.938272046, 0.493677), (1.18937, 0.13957018)]
        )
        amplitude = 1 / (pole**2 - s - 1j * 0.328725260215546 * channels)
        total -= (
            0.5 * ((observed - abs(amplitude) ** 2) / 5) ** 2
            + math.log(5)
            + 0.5 * math.log(2 * math.pi)
        )
    return total


points = [1.402, 1.4051, 1.408]
source = 'm=load_module("../examples/playground.flatppl")\n' + "\n".join(
    f"p{i}=logdensityof(m.Pi_post,record(pole_mass={point}))"
    for i, point in enumerate(points)
)
result = subprocess.run(
    ["node", str(Path(__file__).with_name("evaluate.cjs"))],
    input=json.dumps(
        {"source": source, "bindings": [f"p{i}" for i in range(len(points))]}
    ),
    text=True,
    capture_output=True,
    check=True,
)
actual = json.loads(result.stdout)
for value, point in zip(actual, points):
    assert math.isclose(value, score(point), rel_tol=2e-11, abs_tol=2e-11), (
        point,
        value,
        score(point),
    )
print(json.dumps({"points": points, "logdensity": actual}))
