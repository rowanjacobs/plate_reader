# Simplified model
## Simplifying assumptions
[PK] and [LDH] are high, so their reactions are not rate limiting.

[ATP] and [Glu] are high enough to saturate GS.
## Steady-state GS model

GS-Mg-ADP-Glu-P + NH₄⁺ → GS-Mg-ADP-(Glu-NH₃)-P → GS-Mg-ADP-Pi-Gln

# The gory details
## GS Model
from https://dx.doi.org/10.1021/bi00169a007

GS-Mn + ATP → GS-Mn-ATP + Glu → GS-Mn-ATP-Glu → GS-Mn-ADP-Glu-P + NH₄⁺ → GS-Mn-ADP-(Glu-NH₃)-P → GS-Mn-ADP-Pi-Gln

(We are actually using Mg, not Mn.)

## LDH model
from https://core.ac.uk/download/pdf/81950158.pdf

LDH + NAD⁺ ⇌ LDH-NAD⁺ + lactate ⇌ LDH-NAD⁺-lactate ⇌ LDH-NADH-pyruvate ⇌ LDH-NADH + pyruvate ⇌ LDH + NADH

## PK model
from https://pmc.ncbi.nlm.nih.gov/articles/PMC1184192
```
      PK-PEP                             PK-ATP + Pyr
    ↗↙       ↘                         ↗              ↘
 PK            PK-PEP-ADP → PK-Pyr-ATP                  PK + ATP + Pyr
    ↘        ↗↙                        ↘              ↗
      PK-ADP                             PK-Pyr + ATP
```

## Combined model

```

                                                                     LDH-NAD⁺-lactate ⇌ LDH-NAD⁺ + lactate ⇌ LDH + NAD⁺
                                                                            ⇵ (rxn measured by absorbance change)
                                                                     LDH-NADH-Pyruvate
                                                                            ⇵
      PK-PEP                             PK-ATP + Pyr              Pyr + LDH-NADH ⇌ LDH + NADH
    ↗↙       ↘                         ↗              ↘             ⇵
 PK            PK-PEP-ADP → PK-Pyr-ATP                  PK + ATP + Pyr
    ↘        ↗↙                        ↘              ↗       ⇵
      PK-ADP                             PK-Pyr + ATP        ATP + GS-Mg
                                                                 ⇵
                                                             GS-Mg-ATP + Glu ⇌ GS-Mg-ATP-Glu ⇌ GS-Mg-ADP-Glu-P + NH₄⁺
                                                                                                        ⇵
                                                                                               GS-Mg-ADP-(Glu-NH₃)-P
                                                                                                        ⇵
                                                                                                 GS-Mg-ADP-Pi-Gln
```
