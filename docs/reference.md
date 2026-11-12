# Function reference

## Functions

| Module | Functions |
|---|---|
| `src/angular.flatppl` | `clebschgordan(j1,m1,j2,m2,j,m)`, `clebschgordan_doublearg(two_j1,two_m1,two_j2,two_m2,two_j,two_m)`, `ls_coupling(two_j,two_j1,two_j2,two_l,two_s,two_lambda1,two_lambda2)` |
| `src/angular.flatppl` | `wignerd_matrix(j,cosbeta)`, `wignerd_matrix_doublearg(two_j,cosbeta)` |
| `src/lineshapes.flatppl` | `twobody_phasespace(sigma,ma,mb)`, `resonance_multichannel_breitwigner(sigma,m,gsq,mas,mbs,ls,ds)`, `resonance_bugg_breitwigner(sigma,m,width,sa,gamma)` |
| `src/kinematics.flatppl` | `mass_squared(p)`, `boost_to_rest(p,P)`, `boost_from_rest(p,P)`, `helicity_frame(p,P,child)`, `helicity_angles(p,P,child)` |
| `src/dalitz.flatppl` | `dalitz_cos_theta(k,sigmas,m0,ms)`, `dalitz_cos_zeta(i,k,l,sigmas,m0,ms)` |

The integer-spin angular functions delegate to the doubled-spin functions.
Clebsch-Gordan coefficients use Condon–Shortley phases and return zero for forbidden couplings.
Spins are nonnegative integers, or doubled half-integers. Magnetic arguments use the same doubling convention.
Spin arguments that set array sizes must be fixed before compilation.
The finite factorial sums have no artificial spin cutoff, but cancellation limits accuracy at large spins.

Wigner matrices represent `exp(-i beta Jy)`, with `beta` in `[0,pi]` supplied as `cosbeta`.
Rows and columns descend from `m=j` to `m=-j`.
Their angle derivatives are intended for the interior `-1 < cosbeta < 1`.

## Lineshapes and domains

`sigma` is positive invariant mass squared. Masses are nonnegative, pole masses are positive,
and all masses share one energy unit. Channel vectors have matching lengths.
Orbital momenta are integers from zero through seven. Barrier radii may be zero.
Couplings `gsq` follow the serialization format's signed squared-coupling convention.

`twobody_phasespace` continues each square root from the upper half-plane.
It is positive real above threshold, positive imaginary between thresholds,
and nonpositive real below the pseudothreshold. A principal square root of the
combined Källén polynomial alone would give the wrong last branch.

The multichannel denominator is `m²-sigma-i sum(gsq*rho*z^l/chi_l(z))`,
where `z=d²*kallen(sigma,ma²,mb²)/(4*sigma)`. Two S-wave channels give the Flatté form.
The implementation projects channel values before summation so compiled executors only need real array reductions.

The Bugg helper is the **simplified LHCb Adler-zero form**, not the full Bugg model:
`1/(m²-sigma-i*m*width*(sigma-sa)/(m²-sa)*exp(-gamma*sigma))`.
It requires `sa != m²`. It stays a library helper because this particular form is model-specific.

## Frame and Dalitz conventions

Four-vectors are `[E,px,py,pz]`, with metric `diag(1,-1,-1,-1)` and right-handed spatial axes.
`P` must be future timelike. The two boost functions are inverses and include a stable identity at rest.

Helicity frames use `R(phi,theta,0)`, matching the reference converter.
They do not use the alternative `R(phi,theta,-phi)` phase convention.
`child=2` applies the Jacob–Wick second-child rotation by pi about y. Only children one and two are valid.
`helicity_angles` returns `(costheta=...,phi=...)`. Its transformed spatial momentum must be nonzero.

Dalitz inputs describe a physical decay: `sigmas=[m23²,m31²,m12²]`, `ms=[m1,m2,m3]`,
with `sum(sigmas)=m0²+sum(ms²)`. Chains are `(23)1`, `(31)2`, and `(12)3`.
`dalitz_cos_theta` takes chain `k` from one through three.
`dalitz_cos_zeta` takes particle `i` from zero through three and chains `k,l` from one through three.
Particle zero denotes the parent. Equal chains, massless daughter Wigner rotations, and undefined boundary angles return cosine one.
The functions return cosines only. They do not choose the sign of a Wigner angle.
Physical-domain preconditions are caller obligations. These helpers do not validate an entire decay configuration.

## Example and checks

`examples/lambda1405.flatppl` exposes an invariant-mass input and the Lambda(1405) intensity output.
From the repository root, compile it with the Rust CLI:

```sh
flatppl stablehlo examples/lambda1405.flatppl --dtype f64 -o example.mlir
```

The numerical tests use an existing environment with NumPy and SymPy, plus Node and the JS engine checkout:

```sh
python tests/test_library.py
```

They check CG coefficients against SymPy, Wigner group laws, complex threshold branches,
all eight barrier polynomials, boosts, both child frames, and Dalitz angles against explicit four-vector geometry.
Set `FLATPPL_JS_DIR` if the JS checkout is not the neighboring `flatppl-js` directory.

An existing JAX/Enzyme-JAX environment can also execute the library's compiled test query:

```sh
python tests/run_compiled.py --output compiled-results.json
```

This tests the normal import facade, gradients, and `vmap` in both precisions on the selected JAX device.
`FLATPPL_CLI` selects another compiler. `--modules DIR` reuses prepared MLIR and expected values on another host.

## Sources

The interface follows [FlatPPL PR 234](https://github.com/flatppl/flatppl-design/pull/234),
head `1660121a3463e9856b979f15c826d3d08f6f41d4`, now closed in favor of a community library.
The frame convention and LHCb formulas follow the
[hand-written models and converter](https://github.com/Democratizing-Models/statsmodel-rosetta-stone/tree/31c309d593018c04b14c06c58940548c4bfcd566/src/physics/hadron/amplitude-serialization).
The reference repository's license notice is preserved in `THIRD-PARTY-NOTICES.txt`.

The library uses the MIT license, as do the reference models. See `LICENSE`.

The Dalitz formulas are Eqs. 20, 22, 26, and 29 of
[Mikhasenko et al., PRD 101 (2020) 034033](https://doi.org/10.1103/PhysRevD.101.034033).
The simplified Bugg form follows
[LHCb, PRD 108 (2023) 012023](https://doi.org/10.1103/PhysRevD.108.012023).
