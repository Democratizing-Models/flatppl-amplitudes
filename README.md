# FlatPPL amplitudes

A FlatPPL library for hadron amplitude analysis: coupled-channel lineshapes,
angular-momentum couplings, Wigner matrices, Lorentz boosts, and Dalitz angles.

```flatppl
flatppl_compat = "0.1"
amp = load_module("https://github.com/Democratizing-Models/flatppl-amplitudes/archive/refs/heads/main.zip")

coupling = amp.ls_coupling(3, 1, 2, 2, 1, 1, 0)
rotation = amp.wignerd_matrix_doublearg(1, 0.4)
```

With the Rust CLI, run `flatppl prepare model.flatppl` before compiling a model
that imports the URL. The archive contains the library entry `main.flatppl`
inside GitHub's repository folder. A local checkout also loads with
`load_module("path/to/flatppl-amplitudes")` or `load_module("main.flatppl")`
from a file in that checkout.

The `main` ZIP follows the current branch. To pin the source, use
`https://github.com/Democratizing-Models/flatppl-amplitudes/archive/<commit-sha>.zip`.

See the [function reference](docs/reference.md) for all 15 functions, domains,
phase conventions, and test commands. Spin arguments that determine array
sizes must be fixed before compilation.

[example.flatppl](example.flatppl) evaluates a two-channel Lambda(1405)
lineshape, including the closed-channel continuation. Values, gradients, and
`vmap` pass checks on CPU and GH200 in float32 and float64.

The library follows [the PR 234 proposal](https://github.com/flatppl/flatppl-design/pull/234)
and the [existing LHCb implementations](https://github.com/Democratizing-Models/statsmodel-rosetta-stone/tree/lhcb-amplitude-models/src/physics/hadron/amplitude-serialization).
It uses ordinary FlatPPL modules. Each helper file can also be loaded directly.

MIT license. See [LICENSE](LICENSE) and [third-party notices](THIRD-PARTY-NOTICES.txt).
