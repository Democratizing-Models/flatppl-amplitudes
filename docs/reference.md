# Function reference

All functions below are exported by `main.flatppl`. Arguments are positional or named in the listed order.
Four-vectors are real arrays `[E, px, py, pz]`, with energy first and metric signature `(+,-,-,-)`.
Natural units use $c=1$, so $p^2=E^2-p_x^2-p_y^2-p_z^2$. Masses and four-momentum components share one energy unit.
Spatial axes are right-handed. Rotations are active: they transform vectors while the coordinate axes stay fixed.
The domains below are caller obligations; the library does not validate a whole decay configuration.
Lineshapes are complex amplitudes, not normalized probability densities.

## Functions

| Function | Arguments | Description | Domains |
|---|---|---|---|
| [`clebschgordan`](#clebschgordan) | `j1`, `m1`, `j2`, `m2`, `j`, `m` | Integer-spin Clebsch–Gordan coefficient | nonnegative integer spins, integer projections |
| [`clebschgordan_doublearg`](#clebschgordan_doublearg) | `two_j1`, `two_m1`, `two_j2`, `two_m2`, `two_j`, `two_m` | Clebsch–Gordan coefficient with doubled quantum numbers | nonnegative integer doubled spins, integer doubled projections |
| [`ls_coupling`](#ls_coupling) | `two_j`, `two_j1`, `two_j2`, `two_l`, `two_s`, `two_lambda1`, `two_lambda2` | LS-to-helicity coupling | doubled spins and helicities; nonnegative even `two_l` |
| [`wignerd_matrix`](#wignerd_matrix) | `j`, `cosbeta` | Integer-spin Wigner small-$d$ matrix | nonnegative integers, `interval(-1, 1)` |
| [`wignerd_matrix_doublearg`](#wignerd_matrix_doublearg) | `two_j`, `cosbeta` | Wigner small-$d$ matrix with doubled spin | nonnegative integers, `interval(-1, 1)` |
| [`twobody_phasespace`](#twobody_phasespace) | `sigma`, `ma`, `mb` | Analytically continued two-body phase-space factor | `posreals`, `nonnegreals`, `nonnegreals` |
| [`resonance_multichannel_breitwigner`](#resonance_multichannel_breitwigner) | `sigma`, `m`, `gsq`, `mas`, `mbs`, `ls`, `ds` | Coupled-channel resonance amplitude | positive invariant mass squared and pole mass; aligned channel vectors |
| [`resonance_bugg_breitwigner`](#resonance_bugg_breitwigner) | `sigma`, `m`, `width`, `sa`, `gamma` | Simplified Adler-zero resonance amplitude | positive `sigma`, `m`, `width`; real `sa`, `gamma`; `sa != m^2` |
| [`mass_squared`](#mass_squared) | `p` | Minkowski norm squared | real four-vectors |
| [`boost_to_rest`](#boost_to_rest) | `p`, `P` | Boost into the rest frame of `P` | real four-vectors; future-timelike `P` |
| [`boost_from_rest`](#boost_from_rest) | `p`, `P` | Inverse rest-frame boost | real four-vectors; future-timelike `P` |
| [`helicity_frame`](#helicity_frame) | `p`, `P`, `child` | Four-vector in a helicity frame | real four-vectors; future-timelike `P`; `child` in `{1, 2}` |
| [`helicity_angles`](#helicity_angles) | `p`, `P`, `child` | Polar cosine and azimuth in a helicity frame | helicity-frame domain; nonzero transformed spatial momentum |
| [`dalitz_cos_theta`](#dalitz_cos_theta) | `k`, `sigmas`, `m0`, `ms` | Isobar helicity-angle cosine | `k` in `{1, 2, 3}`; physical three-body decay |
| [`dalitz_cos_zeta`](#dalitz_cos_zeta) | `i`, `k`, `l`, `sigmas`, `m0`, `ms` | Inter-chain Wigner-angle cosine | `i` in `{0, 1, 2, 3}`; chain indices in `{1, 2, 3}`; physical three-body decay |

## Angular momentum

Defined in [`src/angular.flatppl`](../src/angular.flatppl). Angular momenta are measured in units of $\hbar$.
Spin arguments that determine array sizes must be fixed before compilation.
The finite factorial sums have no artificial spin cutoff, but cancellation limits accuracy at large spins.

<a id="clebschgordan"></a>**`clebschgordan(j1, m1, j2, m2, j, m)`** — the real Clebsch–Gordan coefficient in the Condon–Shortley convention:

```math
C^{jm}_{j_1m_1,j_2m_2}=\langle j_1m_1;j_2m_2\mid jm\rangle.
```

Arguments:

- `j1`, `j2`, `j`: nonnegative integer angular momenta.
- `m1`, `m2`, `m`: integer magnetic projections.

Returns zero unless $m=m_1+m_2$, $|m_a|\leq j_a$, $|m|\leq j$, and $|j_1-j_2|\leq j\leq j_1+j_2$.
Equivalent to [`clebschgordan_doublearg`](#clebschgordan_doublearg) with every argument multiplied by two.

<a id="clebschgordan_doublearg"></a>**`clebschgordan_doublearg(two_j1, two_m1, two_j2, two_m2, two_j, two_m)`** — the same coefficient for integer or half-integer spins, with each quantum number passed as its doubled integer value.

Arguments:

- `two_j1`, `two_j2`, `two_j`: nonnegative integers representing $2j_1$, $2j_2$, $2j$.
- `two_m1`, `two_m2`, `two_m`: integers representing $2m_1$, $2m_2$, $2m$.

Returns zero for forbidden projections, triangle couplings, or parity combinations.
In addition to the preceding selection rules, $2j_a+2m_a$, $2j+2m$, and $2j_1+2j_2+2j$ must be even.

<a id="ls_coupling"></a>**`ls_coupling(two_j, two_j1, two_j2, two_l, two_s, two_lambda1, two_lambda2)`** — the real LS-to-helicity coupling for a parent of spin $J$ decaying to spins $j_1,j_2$:

```math
H_{\lambda_1\lambda_2}^{LS;J}
=\sqrt{\frac{2L+1}{2J+1}}\,
C^{S\lambda}_{j_1\lambda_1,j_2(-\lambda_2)}
C^{J\lambda}_{L0,S\lambda},\qquad \lambda=\lambda_1-\lambda_2.
```

Arguments:

- `two_j`, `two_j1`, `two_j2`, `two_s`: nonnegative doubled integer spins $2J,2j_1,2j_2,2S$.
- `two_l`: nonnegative even integer $2L$, where $L$ is orbital angular momentum.
- `two_lambda1`, `two_lambda2`: doubled integer daughter helicities.

The Clebsch–Gordan selection rules apply to both factors. Additional decay-chain phase factors are not included.

<a id="wignerd_matrix"></a>**`wignerd_matrix(j, cosbeta)`** — returns the real $(2j+1)\times(2j+1)$ small Wigner matrix

```math
d^j_{m_1m_2}(\beta)=\langle jm_1\mid e^{-i\beta J_y}\mid jm_2\rangle,
\qquad \beta=\arccos(\mathrm{cosbeta})\in[0,\pi].
```

Arguments:

- `j`: nonnegative integer spin.
- `cosbeta`: real polar-angle cosine in `interval(-1, 1)`.

Rows and columns descend from $m=j$ to $m=-j$. Equivalent to [`wignerd_matrix_doublearg`](#wignerd_matrix_doublearg) with `two_j = 2*j`.
Derivatives with respect to `cosbeta` are intended for the interior $-1<\mathrm{cosbeta}<1$.

<a id="wignerd_matrix_doublearg"></a>**`wignerd_matrix_doublearg(two_j, cosbeta)`** — returns the small Wigner matrix for spin $j=\mathrm{two\_j}/2$.

Arguments:

- `two_j`: nonnegative integer doubled spin $2j$.
- `cosbeta`: real polar-angle cosine in `interval(-1, 1)`.

The result has shape `(two_j + 1, two_j + 1)` and the ordering and rotation convention above.
For spin $1/2$,

```math
d^{1/2}(\beta)=\begin{pmatrix}\cos(\beta/2)&-\sin(\beta/2)\\\sin(\beta/2)&\cos(\beta/2)\end{pmatrix}.
```

## Lineshapes

Defined in [`src/lineshapes.flatppl`](../src/lineshapes.flatppl). Write
$\lambda(x,y,z)=x^2+y^2+z^2-2xy-2yz-2zx$ for the Källén function.

<a id="twobody_phasespace"></a>**`twobody_phasespace(sigma, ma, mb)`** — returns the complex dimensionless two-body phase-space factor

```math
\rho(\sigma;m_a,m_b)=
\sqrt{1-\frac{(m_a+m_b)^2}{\sigma}}\,
\sqrt{1-\frac{(m_a-m_b)^2}{\sigma}}.
```

Arguments:

- `sigma`: positive invariant mass squared, in energy squared.
- `ma`, `mb`: nonnegative daughter masses.

Each square root continues from the upper half-plane: $\sqrt{-u}=i\sqrt{u}$ for $u>0$.
The result is nonnegative real above threshold, positive imaginary between the thresholds, and nonpositive real below the pseudothreshold.
Taking one principal square root of the product would give the wrong sign below the pseudothreshold.
Threshold values are defined, but derivatives can be singular there.

<a id="resonance_multichannel_breitwigner"></a>**`resonance_multichannel_breitwigner(sigma, m, gsq, mas, mbs, ls, ds)`** — returns the coupled-channel amplitude

```math
\mathrm{BW}(\sigma)=\left[m^2-\sigma-i\sum_a g_a^2\rho(\sigma;m_{a1},m_{a2})
\frac{z_a^{\ell_a}}{\chi_{\ell_a}(z_a)}\right]^{-1},\qquad
z_a=\frac{d_a^2\lambda(\sigma,m_{a1}^2,m_{a2}^2)}{4\sigma}.
```

Arguments:

- `sigma`, `m`: positive invariant mass squared and positive pole mass.
- `gsq`: real vector of signed squared-coupling parameters $g_a^2$, in energy squared; its notation does not require nonnegative entries.
- `mas`, `mbs`: nonnegative daughter-mass vectors $m_{a1},m_{a2}$.
- `ls`: integer orbital-momentum vector, with each entry between zero and seven.
- `ds`: nonnegative barrier-radius vector, in inverse energy.

All channel vectors have the same nonzero length. The factor $z^0$ is one, including at zero radius.
$\chi_\ell$ is the Blatt–Weisskopf barrier polynomial, with $\chi_0=1$, $\chi_1=1+z$, $\chi_2=9+3z+z^2$.
The full polynomials through $\ell=7$ follow the FlatPPL `particle-physics` convention in the [kinematics catalogue](https://spec.flatppl.org/#blatt_weisskopf).
The result has units of inverse energy squared. Points where a barrier polynomial or the full amplitude denominator vanishes are excluded.
Two S-wave channels give the Flatté form in this coupling convention. Closed channels use [`twobody_phasespace`](#twobody_phasespace)'s continuation.

<a id="resonance_bugg_breitwigner"></a>**`resonance_bugg_breitwigner(sigma, m, width, sa, gamma)`** — returns the simplified LHCb Adler-zero amplitude

```math
\mathrm{BW}_{\mathrm{Bugg}}(\sigma)=
\left[m^2-\sigma-i m\Gamma\frac{\sigma-s_A}{m^2-s_A}e^{-\gamma\sigma}\right]^{-1}.
```

Arguments:

- `sigma`: positive invariant mass squared.
- `m`, `width`: positive pole mass and width $\Gamma$.
- `sa`: real Adler-zero parameter $s_A$, in energy squared, with $s_A\neq m^2$.
- `gamma`: real exponential coefficient, in inverse energy squared; nonnegative values give damping.

The result is complex with units of inverse energy squared. Its denominator must be nonzero.
This is the simplified form used in the reference LHCb model, not the full Bugg parameterization.

## Four-vectors and helicity frames

Defined in [`src/kinematics.flatppl`](../src/kinematics.flatppl).
For a frame momentum $P$, write $M=\sqrt{(P^0)^2-|\mathbf P|^2}$.
Future-timelike means $P^0>0$ and $M^2>0$.

<a id="mass_squared"></a>**`mass_squared(p)`** — returns the real Minkowski norm squared

```math
p^2=E^2-p_x^2-p_y^2-p_z^2.
```

`p` is a real four-vector. The result has units of energy squared and may be negative for a spacelike vector.

<a id="boost_to_rest"></a>**`boost_to_rest(p, P)`** — returns the four-vector $p'$ after a rotation-free boost into the rest frame of $P$:

```math
E'=\frac{P^0E-\mathbf P\cdot\mathbf p}{M},\qquad
\mathbf p'=\mathbf p+\left[\frac{\mathbf P\cdot\mathbf p}{M(P^0+M)}-\frac{E}{M}\right]\mathbf P.
```

Arguments:

- `p`: real four-vector to transform.
- `P`: future-timelike real frame four-vector.

The result has four real components in the same energy unit. It maps $P$ to $(M,0,0,0)$ and is the identity when $\mathbf P=0$.

<a id="boost_from_rest"></a>**`boost_from_rest(p, P)`** — returns the inverse of [`boost_to_rest`](#boost_to_rest), with components

```math
E'=\frac{P^0E+\mathbf P\cdot\mathbf p}{M},\qquad
\mathbf p'=\mathbf p+\left[\frac{\mathbf P\cdot\mathbf p}{M(P^0+M)}+\frac{E}{M}\right]\mathbf P.
```

Arguments:

- `p`: real four-vector in the rest frame of `P`.
- `P`: future-timelike real frame four-vector.

The result has four real components. Both boosts preserve [`mass_squared`](#mass_squared).

<a id="helicity_frame"></a>**`helicity_frame(p, P, child)`** — returns `p` in the helicity frame defined by `P` and the daughter convention `child`.

Arguments:

- `p`: real four-vector to transform.
- `P`: future-timelike real frame four-vector.
- `child`: integer one or two, selecting the first- or second-child convention.

Let $\epsilon=3-2\,\mathrm{child}$, $\phi=\mathrm{atan2}(\epsilon P_y,\epsilon P_x)$,
and $\theta=\mathrm{atan2}(\sqrt{P_x^2+P_y^2},\epsilon P_z)$.
The transformation is

```math
p'=B_z(-v)\,R_y[-(\mathrm{child}-1)\pi]\,R_y(-\theta)\,R_z(-\phi)\,p,
\qquad v=|\mathbf P|/P^0,
```

where $B_z(-v)$ has $E'=\gamma_v E-\gamma_v v p_z$ and $p'_z=\gamma_v p_z-\gamma_v v E$.
At $\mathbf P=0$, the angle convention sets $\phi=\theta=0$.
The result is a real four-vector. The rotations use the helicity convention $R(\phi,\theta,0)$, with the Jacob–Wick second-child rotation shown explicitly.

<a id="helicity_angles"></a>**`helicity_angles(p, P, child)`** — returns the polar cosine and azimuth of [`helicity_frame(p, P, child)`](#helicity_frame).

Arguments are those of `helicity_frame`, with nonzero transformed spatial momentum $\mathbf q$.
The result is `record(costheta = qz/|q|, phi = atan2(qy, qx))`, where `costheta` lies in $[-1,1]$ and `phi` is in radians.
No angle is defined when $\mathbf q=0$.

## Dalitz angles

Defined in [`src/dalitz.flatppl`](../src/dalitz.flatppl). Let

```math
s_0=m_0^2,\qquad (s_1,s_2,s_3)=(m_{23}^2,m_{31}^2,m_{12}^2).
```

`sigmas = [s1, s2, s3]` and `ms = [m1, m2, m3]` describe a physical three-body decay, with $m_0>0$, $m_a\geq0$ and $s_1+s_2+s_3=s_0+m_1^2+m_2^2+m_3^2$.
The invariant sum alone does not establish physical kinematics. Chains one through three are $(23)1$, $(31)2$, $(12)3$.
Write $Q(x,y,z)=\sqrt{\max(\lambda(x,y,z),0)}$.
Each cosine below is clipped to $[-1,1]$ for numerical roundoff, and is defined as one when its denominator is zero.
These boundary conventions do not validate unphysical inputs. The functions return cosines and do not determine signed Wigner angles.

<a id="dalitz_cos_theta"></a>**`dalitz_cos_theta(k, sigmas, m0, ms)`** — returns the isobar helicity-angle cosine $\cos\theta_k$ in chain $k$.

Arguments:

- `k`: chain index one, two, or three.
- `sigmas`: three invariant masses squared, in the order above.
- `m0`: positive parent mass.
- `ms`: three nonnegative daughter masses.

For the cyclic ordering $(i,j,k)=(2,3,1),(3,1,2),(1,2,3)$,

```math
\cos\theta_k=
\frac{2s_k(s_j-m_k^2-m_i^2)-(s_k+m_i^2-m_j^2)(s_0-s_k-m_k^2)}
{Q(s_0,m_k^2,s_k)\,Q(s_k,m_i^2,m_j^2)}.
```

The result is real and dimensionless, with the boundary convention above.

<a id="dalitz_cos_zeta"></a>**`dalitz_cos_zeta(i, k, l, sigmas, m0, ms)`** — returns the cosine of the Wigner rotation for particle `i` between chains `k` and `l`.

Arguments:

- `i`: particle index zero through three; zero denotes the parent.
- `k`, `l`: chain indices one through three.
- `sigmas`, `m0`, `ms`: the physical three-body inputs defined above.

For equal chains, the result is one. For distinct chains, let $n=6-k-l$ be the remaining daughter index.
For the parent,

```math
\cos\zeta_0^{kl}=\frac{(s_0+m_k^2-s_k)(s_0+m_l^2-s_l)-2s_0(s_n-m_k^2-m_l^2)}
{Q(s_0,m_k^2,s_k)\,Q(s_0,m_l^2,s_l)}.
```

For a massive daughter that is the spectator of chain $k$,

```math
\cos\zeta_k^{kl}=\frac{2m_k^2(s_n-s_0-m_n^2)+(s_0+m_k^2-s_k)(s_l-m_k^2-m_n^2)}
{Q(s_0,m_k^2,s_k)\,Q(s_l,m_k^2,m_n^2)}.
```

The case $i=l$ follows by exchanging $k$ and $l$. For the remaining massive daughter,

```math
\cos\zeta_n^{kl}=\frac{2m_n^2(m_k^2+m_l^2-s_n)+(s_k-m_n^2-m_l^2)(s_l-m_n^2-m_k^2)}
{Q(s_k,m_n^2,m_l^2)\,Q(s_l,m_n^2,m_k^2)}.
```

For a massless daughter, the result is one by convention. All results are real and dimensionless, with the boundary convention above.

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

The frame convention and LHCb formulas follow the
[hand-written models and converter](https://github.com/Democratizing-Models/statsmodel-rosetta-stone/tree/31c309d593018c04b14c06c58940548c4bfcd566/src/physics/hadron/amplitude-serialization).
The reference repository's license notice is preserved in `THIRD-PARTY-NOTICES.txt`.

The library uses the MIT license, as do the reference models. See `LICENSE`.

The Dalitz formulas are Eqs. 20, 22, 26, and 29 of
[Mikhasenko et al., PRD 101 (2020) 034033](https://doi.org/10.1103/PhysRevD.101.034033).
The simplified Bugg form follows
[LHCb, PRD 108 (2023) 012023](https://doi.org/10.1103/PhysRevD.108.012023).
