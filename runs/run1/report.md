## `sustainable`: overall (95% CI over bases)

| judge | set | n | auroc | d_gc | w_gc | d_gi | d_si | d_ki | loc_lift | retest_r | cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| checklist | canonical | 640 | 0.833 | 0.000 | 0.500 | 0.000 | 1.000 | 1.000 | 0.000 | — | 0.000 |
| checklist | random | 2400 | 0.833 | 0.000 | 0.500 | 0.000 | 1.000 | 1.000 | 0.000 | — | 0.000 |
| jev | canonical | 640 | 0.533 | -0.002 [-0.01, 0.00] | 0.465 [0.37, 0.57] | -0.005 | 0.019 [0.02, 0.02] | 0.010 [0.00, 0.01] | 0.779 | 0.958 | 0.102 |
| jev | random | 2400 | 0.538 | -0.001 [-0.00, 0.00] | 0.525 [0.48, 0.56] | -0.002 | 0.022 [0.02, 0.03] | 0.007 [0.00, 0.01] | 0.736 | 0.955 | 0.396 |

## `coherent`: overall (95% CI over bases)

| judge | set | n | auroc | d_gc | w_gc | d_gi | d_si | d_ki | loc_lift | retest_r | cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| checklist | canonical | 640 | 0.833 | 0.000 | 0.500 | 0.000 | 1.000 | 1.000 | 0.000 | — | 0.000 |
| checklist | random | 2400 | 0.833 | 0.000 | 0.500 | 0.000 | 1.000 | 1.000 | 0.000 | — | 0.000 |
| jev | canonical | 640 | 0.548 | 0.007 [0.00, 0.01] | 0.574 [0.52, 0.64] | -0.004 | 0.031 [0.03, 0.04] | 0.008 [0.00, 0.01] | 0.779 | 0.958 | 0.102 |
| jev | random | 2400 | 0.549 | 0.001 [-0.00, 0.00] | 0.499 [0.45, 0.54] | 0.001 | 0.036 [0.03, 0.04] | 0.011 [0.01, 0.02] | 0.736 | 0.955 | 0.396 |

## `sustainable` by rendering cell

| judge | set | names | register | rule | n | d_gc | w_gc | d_gi | d_si | d_ki | fam_gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jev | canonical | familiar | abstract | implicit | 80 | -0.002 | 0.531 | -0.008 | 0.016 | 0.010 | — |
| jev | canonical | familiar | abstract | stated | 80 | -0.016 | 0.250 | -0.011 | 0.018 | 0.014 | — |
| jev | canonical | familiar | eco | implicit | 80 | 0.007 | 0.562 | -0.004 | 0.042 | 0.017 | — |
| jev | canonical | familiar | eco | stated | 80 | -0.001 | 0.438 | -0.013 | 0.024 | -0.001 | — |
| jev | canonical | nonce | abstract | implicit | 80 | 0.004 | 0.531 | 0.008 | 0.009 | 0.001 | — |
| jev | canonical | nonce | abstract | stated | 80 | -0.017 | 0.406 | -0.004 | 0.021 | 0.021 | — |
| jev | canonical | nonce | eco | implicit | 80 | 0.004 | 0.562 | -0.002 | 0.014 | 0.011 | — |
| jev | canonical | nonce | eco | stated | 80 | 0.001 | 0.438 | -0.007 | 0.012 | 0.004 | — |
| jev | random | familiar | abstract | implicit | 300 | -0.003 | 0.417 | -0.000 | 0.016 | 0.012 | — |
| jev | random | familiar | abstract | stated | 300 | 0.008 | 0.675 | 0.000 | 0.019 | 0.012 | — |
| jev | random | familiar | eco | implicit | 300 | -0.006 | 0.450 | -0.003 | 0.034 | 0.007 | — |
| jev | random | familiar | eco | stated | 300 | -0.004 | 0.458 | -0.001 | 0.042 | 0.007 | — |
| jev | random | nonce | abstract | implicit | 300 | 0.000 | 0.575 | -0.001 | 0.009 | 0.001 | — |
| jev | random | nonce | abstract | stated | 300 | -0.006 | 0.517 | -0.012 | 0.016 | 0.007 | — |
| jev | random | nonce | eco | implicit | 300 | 0.001 | 0.583 | 0.002 | 0.021 | 0.006 | — |
| jev | random | nonce | eco | stated | 300 | 0.003 | 0.525 | 0.001 | 0.016 | 0.007 | — |

## Familiarity

| judge | set | fam_gap | fam_beta |
|---|---|---|---|
| jev | canonical | 0.091 | -0.279 |
| jev | random | 0.045 | -0.628 |

## Dose-response (random set, `sustainable`)

| judge | n_entities | n | d_gc | w_gc | d_gi | d_si | d_ki |
|---|---|---|---|---|---|---|---|
| jev | 7 | 480 | -0.006 | 0.510 | -0.005 | 0.033 | 0.019 |
| jev | 9 | 480 | -0.002 | 0.516 | -0.000 | 0.031 | 0.007 |
| jev | 11 | 480 | 0.004 | 0.599 | 0.001 | 0.019 | 0.003 |
| jev | 13 | 480 | 0.002 | 0.547 | -0.004 | 0.014 | 0.006 |
| jev | 15 | 480 | -0.001 | 0.453 | -0.000 | 0.011 | 0.003 |

## Batch filtering on unmatched candidates (random set; batches of 50, keep top 5, 20% complete)

| judge | score | contrast | d | d_per_sd | base_rate | precision_top | enrichment |
|---|---|---|---|---|---|---|---|
| checklist | sustainable | intact vs source | 1.000 | — | 0.200 | 1.000 | 5.000 |
| checklist | sustainable | control vs global | 0.000 | — | 0.200 | 0.202 | 1.009 |
| checklist | coherent | intact vs source | 1.000 | — | 0.200 | 1.000 | 5.000 |
| checklist | coherent | control vs global | 0.000 | — | 0.200 | 0.202 | 1.009 |
| jev | sustainable | intact vs source | 0.022 | 0.278 | 0.200 | 0.247 | 1.236 |
| jev | sustainable | control vs global | -0.001 | -0.009 | 0.200 | 0.193 | 0.966 |
| jev | coherent | intact vs source | 0.036 | 0.419 | 0.200 | 0.274 | 1.368 |
| jev | coherent | control vs global | 0.001 | 0.006 | 0.200 | 0.196 | 0.981 |
