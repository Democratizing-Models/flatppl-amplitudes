# LHCb reference values

`lhcb.json` records values from the source models at commit
[`31c309d`](https://github.com/Democratizing-Models/statsmodel-rosetta-stone/tree/31c309d593018c04b14c06c58940548c4bfcd566/src/physics/hadron/amplitude-serialization).
The source’s independent `check_flatppl.py` evaluator reproduces all 34 validation checks from the published model JSON files.

Each case records complex amplitudes as adjacent real and imaginary components, followed by the intensity.
The points include the source validation points and two interior reference-coordinate configurations.
`coordinate_cases` and `rates` check the complete coordinate-to-rate path.
`rate_gradients` use central differences of the source rate with a step of 1e-6 in each coordinate.
