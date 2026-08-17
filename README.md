# Clinic acquisition stress model

Run:

```bash
python3 -m unittest -v
python3 clinic_stress_model.py
```

The default case reflects the most recent assumptions in the supplied discussion:

| Input | Default |
| --- | ---: |
| Fixed annual cost | 70억 |
| Variable cost | revenue × 30% |
| Combined owner draw | revenue × 10%, paid before company profit |
| Owner effective tax | 38% |
| Corporate + local income tax | progressive schedule + 10% local surcharge |
| Unpaid acquisition balance | 90억 |
| Doctors / operating days | 10 / 28 per month |
| Capacity case | 25 patients per doctor-day × 15만원 realised revenue |

Money values in the JSON output are **억 원**. `per_owner_monthly_take_home`
is therefore 0.3255 = 3,255만원 per owner per month.

## Model logic

For annual revenue `R`, the model uses:

```text
owner pre-tax draw       = R × 10%
EBIT                     = R - variable costs - owner draw - fixed costs
corporate tax            = progressive national corporate tax + 10% local surcharge
cash available for debt  = EBIT - corporate tax
per-owner net monthly    = owner draw × (1 - owner tax) / 2 / 12
```

Acquisition principal is **not** deducted when calculating corporate tax.
The 6, 7, and 10-year thresholds are solved using post-corporate-tax cash
available to repay the 90억 balance. This avoids the common error of treating
principal repayment as a deductible expense.

At the default 10-doctor, 28-day capacity case, 25 patients per doctor-day
and 15만원 realised revenue per encounter imply:

- 250 patients per day, 7,000 per month
- 10.5억 monthly sales
- about 3,255만원 monthly take-home per owner
- about 4.65억 annual cash for principal, before reserve capex and working-capital changes
- about 19.4 years to repay 90억 if that exact sales and cost level persists

The default 7-year threshold is approximately **11.95억 monthly revenue**;
the 6-year threshold is about **12.33억**. These outputs are intentionally
higher than a pre-tax calculation because corporate tax is included.

## What the model cannot infer

The included simulation is a transparent sensitivity exercise, not a
statistical test and cannot substantiate a claim such as `p < 0.05`. Its
patient-volume and price ranges are priors (18/25/32 patients per doctor-day,
12/15/18만원 per encounter). Replace them with 12–24 months of:

1. monthly revenue recognised (not payment-processor GMV);
2. unique visits, procedure visits, refunds, and realised revenue per visit;
3. rostered doctor-days and actual doctor/employee payroll including employer
   contributions, severance, incentives, and agency fees;
4. rent, CAM, marketing, consumables, card fees, capex replacement, VAT, and
   working-capital movements;
5. the signed payment waterfall: whether the 90% is gross revenue, revenue
   after operating costs, an MSO fee, or a capped purchase-price instalment;
6. personal guarantee, missed-payment, extension, default, and ownership
   transfer clauses.

The legal and tax treatment must be reviewed from the actual contracts by
Korean healthcare counsel and a tax professional. The output is not evidence
that an MSO structure is lawful or that repayment/ownership transfer will occur.

## Example

```bash
python3 clinic_stress_model.py \
  --doctors 10 --days 28 --patients-per-doctor-day 28 \
  --revenue-per-patient 150000 --fixed-cost 70
```
