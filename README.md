# flatppl-amplitudes

[Function reference](docs/reference.md) · [Live example](https://live.flatppl.org/#model=https%3A%2F%2Fraw.githubusercontent.com%2Fflatppl-community%2Fflatppl-amplitudes%2Fmain%2Fexamples%2Fplayground.flatppl&target=Pi_post)

Hadron amplitude analysis for FlatPPL: coupled-channel lineshapes, angular-momentum couplings, Wigner matrices, Lorentz boosts, and Dalitz angles. Library version **0.1**.

```flatppl
flatppl_compat = "0.1"
amp = load_module("https://raw.githubusercontent.com/flatppl-community/flatppl-amplitudes/858849d2d32dd0593eba37ca3e1d955f497ef796/main.flatppl")

coupling = amp.ls_coupling(
    two_j = 3, two_j1 = 1, two_j2 = 2,
    two_l = 2, two_s = 1, two_lambda1 = 1, two_lambda2 = 0)
rotation = amp.wignerd_matrix_doublearg(two_j = 1, cosbeta = 0.4)
```

The example uses doubled angular momenta. The coupling describes a spin-3/2 decay to spins 1/2 and 1, with orbital momentum 1. Array dimensions must be fixed before compilation.

The [resonance example](examples/playground.flatppl) infers a pole mass from synthetic intensities. The [LHCb examples](docs/lhcb-examples.md) present kinematics, amplitude models, and observables in that order.

See the reference for definitions, conventions, numerical limits, and validation. The library uses the [MIT license](LICENSE), with [third-party notices](THIRD-PARTY-NOTICES.txt).
