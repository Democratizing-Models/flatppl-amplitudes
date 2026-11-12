# LHCb decay examples

These ports use the published parameters of the
[source models](https://github.com/Democratizing-Models/statsmodel-rosetta-stone/tree/31c309d593018c04b14c06c58940548c4bfcd566/src/physics/hadron/amplitude-serialization).
They retain every decay chain and the source models’ helicity-frame conventions.

| Example | Decay | Chains | Coordinates |
|---|---|---:|---:|
| [Λc](../examples/lhcb/lc2ppik-lhcb-2683025.flatppl) | Λc+ → p π+ K− | 26 | 5 |
| [Λb](../examples/lhcb/lb2pkg-lhcb-2765817.flatppl) | Λb0 → p K− γ | 74 | 5 |
| [B+, C−](../examples/lhcb/b2dxdk-lhcb-2794793-Cminus.flatppl) | B+ → D0 π+ D− K+ | 19 | 7 |
| [B+, C+](../examples/lhcb/b2dxdk-lhcb-2794793-Cplus.flatppl) | B+ → anti-D0 π− D+ K+ | 15 | 7 |

Each entry file has three parts, in this order:

1. **Kinematics:** masses, reference decay coordinates, and final-state four-momenta.
2. **Amplitude model:** load the matching model from `examples/lhcb/models/` and evaluate its complex helicity amplitudes.
3. **Observable:** sum squared amplitudes over external helicities, then multiply by the phase-space density.

The model modules contain the detailed resonance parameters and chain sums.
They use the library for LS couplings, Wigner functions, Dalitz angles, helicity frames, and coupled-channel lineshapes.
The small support modules construct reference momenta and express the standard mass-dependent Breit–Wigner formula.
The scalar Wigner adapter sums the library's existing terms for each requested helicity pair, avoiding unused matrix entries.
These adapters let the examples compile without dedicated scalar Wigner or Breit–Wigner engine primitives.

The B+ examples fix the D* mass to 2.01026 GeV, as the source models do.
They pass that fixed mass directly to the amplitude, avoiding roundoff from reconstructing it from four-momenta.
Their narrow lineshape has a width of 1e-6 GeV. Use float64 when checking arbitrary four-momenta near that peak.

## Compile a rate

From the repository root:

```sh
flatppl stablehlo examples/lhcb/lc2ppik-lhcb-2683025.flatppl --dtype f64 -o lc-rate.mlir
```

`inputs` lists the reference coordinates in the function’s argument order.
`outputs = rate` selects the unnormalised decay rate, so this query needs no normalisation integral.
The examples also retain `decay_distribution`, `event_distribution`, and the source event-generation recipe.
The unary adapters `fn(rate_fn(_))` and `fn(momenta_fn(_))` pass the coordinate record to the corresponding ordinary call.

## Check the ports

The JS checks compare complex amplitudes, intensities, lineshapes, and coordinate rates with frozen source results:

```sh
python tests/test_examples.py
```

An existing JAX/Enzyme-JAX environment can check compiled rates, gradients, and batching:

```sh
python tests/run_examples.py --prepare --modules /tmp/lhcb-compiled
python tests/run_examples.py --modules /tmp/lhcb-compiled --output /tmp/lhcb-results.json
```

Preparation emits CPU and GPU modules in both precisions. Copy that directory to another host to test its selected JAX device.
Large spin sums make the first derivative compilation expensive. Reuse compiled callables; the runner records cold and warm times separately.
`FLATPPL_CLI` and `FLATPPL_JS_DIR` select the compiler and JS checkout.
The frozen references and their provenance live in `tests/fixtures/`.
