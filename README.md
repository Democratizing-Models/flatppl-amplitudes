# FlatPPL amplitudes

A FlatPPL library for hadron amplitude analysis: coupled-channel lineshapes,
angular-momentum couplings, Wigner matrices, Lorentz boosts, and Dalitz angles.

```flatppl
flatppl_compat = "0.1"
amp = load_module("https://github.com/Democratizing-Models/flatppl-amplitudes/archive/refs/heads/main.zip")

coupling = amp.ls_coupling(
    two_j = 3, two_j1 = 1, two_j2 = 2,
    two_l = 2, two_s = 1, two_lambda1 = 1, two_lambda2 = 0)
rotation = amp.wignerd_matrix_doublearg(two_j = 1, cosbeta = 0.4)
```

The coupling describes a spin-3/2 parent decaying to spins 1/2 and 1, with
orbital momentum 1, total spin 1/2, and helicities (1/2, 0). The example uses
doubled angular momenta.

With the Rust CLI, run `flatppl prepare model.flatppl` and approve the URL before
compiling a model that imports it. The source ZIP contains `main.flatppl` inside
GitHub's repository folder. A local checkout also loads with
`load_module("path/to/flatppl-amplitudes")` or `load_module("main.flatppl")`
from a file in that checkout.

The URL follows the current branch. Use `/archive/<commit-sha>.zip` to pin it.
GitHub's redirect and CORS policy currently prevent direct archive imports in
the web playground.

See the [function reference](docs/reference.md) for all 15 functions, domains,
phase conventions, and test commands. Spin arguments that determine array
sizes must be fixed before compilation.

[The Lambda(1405) example](examples/lambda1405.flatppl) evaluates a two-channel
lineshape, including the closed-channel continuation. Values, gradients, and
`vmap` pass checks on CPU and GH200 in float32 and float64.

The [complete LHCb examples](docs/lhcb-examples.md) cover Λc, Λb, and both B+ amplitudes,
with kinematics, amplitude model, and observable presented in that order.
Each helper module in `src/` can also be loaded directly.

MIT license. See [LICENSE](LICENSE) and [third-party notices](THIRD-PARTY-NOTICES.txt).
