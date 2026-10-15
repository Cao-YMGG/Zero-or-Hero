# Night session vs the next day

Alpaca SIP 5-minute bars, extended hours. night = prior close -> last print before 09:30; ah = 16:00-20:00; ovn = 20:00-04:00 (last after-hours print -> first pre-market print); pre = 04:00-09:30; day = open -> close; first = open -> 10:30; rest = 10:30 -> close. 'agree' = share of days whose move went the same way as the night.

Data through 2026-10-14.

## SPY

### Correlations with the day (open -> close)

| period | n | night | ah | ovn | pre | night vs first hour | first hour vs rest |
|---|---|---|---|---|---|---|---|
| last 3 months | 65 | +0.12 | -0.07 | +0.01 | +0.21 | -0.08 | +0.05 |
| last year | 252 | -0.07 | -0.15 | -0.06 | +0.06 | -0.06 | -0.05 |
| since 2024-02 | 680 | -0.11 | -0.13 | -0.08 | +0.01 | -0.03 | +0.07 |

### Day move by night bucket

| period | night bucket | n | day avg | day median | day up% | agree with night |
|---|---|---|---|---|---|---|
| last 3 months | night <= -0.5% | 6 | +0.00% | -0.04% | 33% | 67% |
| last 3 months | -0.5% .. -0.2% | 10 | -0.15% | -0.18% | 30% | 70% |
| last 3 months | flat (|night| < 0.2%) | 22 | -0.18% | -0.19% | 36% | 50% |
| last 3 months | +0.2% .. +0.5% | 17 | +0.22% | +0.28% | 65% | 65% |
| last 3 months | night >= +0.5% | 10 | -0.08% | -0.09% | 30% | 30% |
| last year | night <= -0.5% | 29 | +0.09% | -0.01% | 48% | 52% |
| last year | -0.5% .. -0.2% | 39 | -0.06% | -0.05% | 46% | 54% |
| last year | flat (|night| < 0.2%) | 89 | -0.01% | +0.03% | 51% | 44% |
| last year | +0.2% .. +0.5% | 51 | +0.11% | +0.13% | 57% | 57% |
| last year | night >= +0.5% | 44 | -0.08% | -0.13% | 41% | 41% |
| since 2024-02 | night <= -0.5% | 76 | +0.16% | +0.03% | 51% | 49% |
| since 2024-02 | -0.5% .. -0.2% | 91 | +0.04% | +0.07% | 56% | 44% |
| since 2024-02 | flat (|night| < 0.2%) | 261 | -0.01% | -0.02% | 49% | 46% |
| since 2024-02 | +0.2% .. +0.5% | 148 | +0.03% | +0.07% | 55% | 55% |
| since 2024-02 | night >= +0.5% | 104 | -0.11% | -0.03% | 49% | 49% |

### Night move given back in the pre-market

| period | pattern | n | day avg | day median | day up% |
|---|---|---|---|---|---|
| last 3 months | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 1 | -1.41% | -1.41% | 0% |
| last 3 months | night up, pre-market extends >= 0.2% | 4 | -0.01% | -0.09% | 25% |
| last 3 months | night down, pre-market extends <= -0.2% | 2 | +0.00% | +0.00% | 50% |
| last year | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 6 | -0.68% | -0.81% | 17% |
| last year | night up, pre-market extends >= 0.2% | 14 | -0.36% | -0.15% | 21% |
| last year | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 12 | +0.46% | +0.55% | 58% |
| last year | night down, pre-market extends <= -0.2% | 8 | +0.10% | +0.00% | 50% |
| since 2024-02 | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 19 | +0.04% | +0.19% | 53% |
| since 2024-02 | night up, pre-market extends >= 0.2% | 39 | -0.27% | -0.12% | 41% |
| since 2024-02 | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 32 | +0.66% | +0.58% | 59% |
| since 2024-02 | night down, pre-market extends <= -0.2% | 31 | -0.14% | -0.09% | 48% |

### Macro days vs other days (night >= 0.2% either way)

| period | days | n | agree with night | day avg in night's direction |
|---|---|---|---|---|
| last 3 months | macro | 6 | 33% | -0.04% |
| last 3 months | other | 37 | 62% | +0.13% |
| last year | macro | 22 | 45% | -0.02% |
| last year | other | 141 | 52% | +0.02% |
| since 2024-02 | macro | 53 | 60% | +0.18% |
| since 2024-02 | other | 366 | 48% | -0.08% |

## QQQ

### Correlations with the day (open -> close)

| period | n | night | ah | ovn | pre | night vs first hour | first hour vs rest |
|---|---|---|---|---|---|---|---|
| last 3 months | 65 | +0.04 | -0.04 | +0.02 | +0.07 | -0.10 | +0.00 |
| last year | 252 | -0.03 | -0.12 | +0.00 | +0.05 | -0.11 | -0.01 |
| since 2024-02 | 680 | -0.07 | -0.10 | -0.01 | -0.02 | -0.09 | +0.06 |

### Day move by night bucket

| period | night bucket | n | day avg | day median | day up% | agree with night |
|---|---|---|---|---|---|---|
| last 3 months | night <= -0.5% | 17 | +0.01% | +0.04% | 53% | 47% |
| last 3 months | -0.5% .. -0.2% | 5 | -0.37% | -0.49% | 20% | 80% |
| last 3 months | flat (|night| < 0.2%) | 11 | -0.04% | -0.22% | 45% | 55% |
| last 3 months | +0.2% .. +0.5% | 14 | -0.12% | -0.18% | 29% | 29% |
| last 3 months | night >= +0.5% | 18 | +0.09% | -0.12% | 39% | 39% |
| last year | night <= -0.5% | 61 | -0.03% | -0.08% | 49% | 51% |
| last year | -0.5% .. -0.2% | 25 | -0.09% | +0.11% | 52% | 48% |
| last year | flat (|night| < 0.2%) | 51 | +0.14% | +0.23% | 59% | 47% |
| last year | +0.2% .. +0.5% | 46 | -0.12% | -0.08% | 43% | 43% |
| last year | night >= +0.5% | 69 | +0.06% | -0.08% | 49% | 49% |
| since 2024-02 | night <= -0.5% | 119 | +0.01% | +0.15% | 55% | 45% |
| since 2024-02 | -0.5% .. -0.2% | 79 | +0.02% | +0.15% | 53% | 47% |
| since 2024-02 | flat (|night| < 0.2%) | 183 | +0.07% | +0.10% | 55% | 51% |
| since 2024-02 | +0.2% .. +0.5% | 131 | -0.01% | -0.01% | 49% | 49% |
| since 2024-02 | night >= +0.5% | 168 | -0.06% | +0.03% | 52% | 52% |

### Night move given back in the pre-market

| period | pattern | n | day avg | day median | day up% |
|---|---|---|---|---|---|
| last 3 months | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 6 | +0.20% | -0.10% | 33% |
| last 3 months | night up, pre-market extends >= 0.2% | 9 | +0.38% | +0.13% | 56% |
| last 3 months | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 3 | -0.53% | -0.53% | 0% |
| last 3 months | night down, pre-market extends <= -0.2% | 5 | -0.10% | -0.36% | 40% |
| last year | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 17 | +0.15% | -0.04% | 41% |
| last year | night up, pre-market extends >= 0.2% | 34 | +0.13% | +0.09% | 53% |
| last year | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 24 | +0.25% | +0.39% | 58% |
| last year | night down, pre-market extends <= -0.2% | 22 | -0.20% | -0.32% | 36% |
| since 2024-02 | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 47 | +0.40% | +0.35% | 57% |
| since 2024-02 | night up, pre-market extends >= 0.2% | 76 | -0.15% | +0.04% | 53% |
| since 2024-02 | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 47 | +0.14% | +0.29% | 53% |
| since 2024-02 | night down, pre-market extends <= -0.2% | 48 | -0.16% | -0.37% | 42% |

### Macro days vs other days (night >= 0.2% either way)

| period | days | n | agree with night | day avg in night's direction |
|---|---|---|---|---|
| last 3 months | macro | 7 | 29% | +0.05% |
| last 3 months | other | 47 | 45% | +0.03% |
| last year | macro | 25 | 40% | -0.02% |
| last year | other | 176 | 49% | +0.02% |
| since 2024-02 | macro | 64 | 58% | +0.26% |
| since 2024-02 | other | 433 | 47% | -0.07% |

## single stocks (8)

### Correlations with the day (open -> close)

| period | n | night | ah | ovn | pre | night vs first hour | first hour vs rest |
|---|---|---|---|---|---|---|---|
| last 3 months | 520 | +0.06 | +0.03 | +0.06 | +0.03 | +0.12 | +0.07 |
| last year | 2016 | +0.02 | -0.02 | +0.02 | +0.04 | +0.04 | +0.01 |
| since 2024-02 | 5440 | -0.04 | -0.04 | -0.01 | -0.04 | -0.03 | +0.03 |

### Day move by night bucket

| period | night bucket | n | day avg | day median | day up% | agree with night |
|---|---|---|---|---|---|---|
| last 3 months | night <= -0.5% | 133 | +0.15% | +0.00% | 50% | 50% |
| last 3 months | -0.5% .. -0.2% | 52 | -0.19% | -0.29% | 44% | 56% |
| last 3 months | flat (|night| < 0.2%) | 91 | -0.01% | -0.16% | 45% | 60% |
| last 3 months | +0.2% .. +0.5% | 59 | -0.16% | -0.12% | 47% | 47% |
| last 3 months | night >= +0.5% | 185 | +0.07% | +0.02% | 51% | 51% |
| last year | night <= -0.5% | 567 | +0.08% | +0.04% | 51% | 49% |
| last year | -0.5% .. -0.2% | 209 | -0.07% | +0.04% | 51% | 49% |
| last year | flat (|night| < 0.2%) | 370 | -0.05% | -0.00% | 50% | 50% |
| last year | +0.2% .. +0.5% | 207 | -0.10% | -0.13% | 45% | 45% |
| last year | night >= +0.5% | 663 | +0.13% | +0.06% | 52% | 52% |
| since 2024-02 | night <= -0.5% | 1401 | +0.06% | +0.11% | 53% | 47% |
| since 2024-02 | -0.5% .. -0.2% | 559 | +0.05% | +0.04% | 51% | 49% |
| since 2024-02 | flat (|night| < 0.2%) | 1039 | -0.04% | +0.02% | 51% | 50% |
| since 2024-02 | +0.2% .. +0.5% | 665 | -0.10% | -0.05% | 47% | 47% |
| since 2024-02 | night >= +0.5% | 1776 | +0.08% | +0.07% | 52% | 52% |

### Night move given back in the pre-market

| period | pattern | n | day avg | day median | day up% |
|---|---|---|---|---|---|
| last 3 months | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 66 | -0.02% | -0.13% | 47% |
| last 3 months | night up, pre-market extends >= 0.2% | 91 | +0.09% | +0.06% | 52% |
| last 3 months | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 39 | -0.45% | -0.49% | 36% |
| last 3 months | night down, pre-market extends <= -0.2% | 58 | +0.31% | +0.26% | 55% |
| last year | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 275 | -0.07% | -0.12% | 48% |
| last year | night up, pre-market extends >= 0.2% | 280 | +0.34% | +0.09% | 55% |
| last year | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 229 | +0.13% | +0.04% | 50% |
| last year | night down, pre-market extends <= -0.2% | 201 | +0.07% | +0.12% | 51% |
| since 2024-02 | night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2% | 719 | +0.12% | +0.04% | 51% |
| since 2024-02 | night up, pre-market extends >= 0.2% | 763 | +0.10% | +0.12% | 54% |
| since 2024-02 | night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2% | 523 | +0.08% | +0.00% | 50% |
| since 2024-02 | night down, pre-market extends <= -0.2% | 496 | +0.06% | +0.08% | 51% |

### Macro days vs other days (night >= 0.2% either way)

| period | days | n | agree with night | day avg in night's direction |
|---|---|---|---|---|
| last 3 months | macro | 51 | 57% | +0.29% |
| last 3 months | other | 378 | 50% | -0.06% |
| last year | macro | 199 | 53% | +0.04% |
| last year | other | 1447 | 49% | +0.02% |
| since 2024-02 | macro | 545 | 56% | +0.22% |
| since 2024-02 | other | 3856 | 48% | -0.04% |

