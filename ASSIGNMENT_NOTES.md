# Assignment Notes — Testing the SpeedController

All expected outputs were derived from the written requirements in
`README.md` (Appendix A), which is the oracle for this lab (no
`legacy_speed_controller.py` module is present). A fixed speed limit of
60 km/h is used so each test varies one input against a known-valid
baseline: `clear` / traffic 20 / slope 0 / safety off => 60.00.

---

## Step 1 — Run your first test

Running the starter test as shipped produced one failure:

```
FAIL: test_example ... AssertionError: 60.0 != 50 : Expected value does not match
Ran 1 test in 0.001s
FAILED (failures=1)
```

The function returned `60.0` for `update_speed('clear', 20, 0)` with
safety mode off. Per the requirements this is correct: a `clear` road
leaves the base speed unchanged (x1.0), a traffic density of 20 is below
50 so no reduction applies, and a slope of 0 has no effect, giving
`60 * 1.0 = 60.00`. The starter test asserted `50`, which does not match
the specification.

**Fix applied:** the *test* was wrong, not the production code, so the
expected value was corrected (50 -> 60). No production code was changed
to make this test pass. The corrected baseline case is now
`test_clear_road_nominal` in `test_black_box.py`.

---

## Step 2 — Category Partition

Categories for `safety_mode` and `road_condition`, by how each affects
the output.

| Parameter | Category | Example Value | Expected Behavior |
|-----------|----------|---------------|-------------------|
| safety_mode | enabled | `True` | Target speed clamped to at most `speed_limit - 10` |
| safety_mode | disabled | `False` | Target speed clamped to at least 0 (no upper cap from safety mode) |
| road_condition | clear | `'clear'` | Base speed unchanged (multiplier 1.0) |
| road_condition | wet | `'wet'` | Base speed x 0.85 |
| road_condition | icy | `'icy'` | Base speed x 0.6 |
| road_condition | invalid | `'foggy'` | Raises `ValueError` |

---

## Step 3 — Boundary Value Analysis

Boundary values for `traffic_density` (valid range 0–100; behaviour
changes at 50 and 80) and `slope_angle` (valid range -10 to +10).

### Nominal Values

| Parameter | Boundary | Value | Expected Behavior |
|-----------|----------|-------|-------------------|
| traffic_density | min | 0 | No reduction (below 50) |
| traffic_density | just below first threshold | 49 | No reduction |
| traffic_density | first threshold (incl.) | 50 | Reduce by 10 |
| traffic_density | top of -10 band | 80 | Reduce by 10 |
| traffic_density | just above 80 | 81 | Reduce by 20 |
| traffic_density | max | 100 | Reduce by 20 |
| slope_angle | min (downhill) | -10 | Increase by 10 |
| slope_angle | just below flat | -1 | Increase by 1 |
| slope_angle | flat | 0 | No change |
| slope_angle | just above flat | 1 | Decrease by 1 |
| slope_angle | max (uphill) | 10 | Decrease by 10 |

### Invalid Values

Each invalid test case holds exactly one out-of-range parameter.

| Parameter | Boundary | Value | Expected Behavior |
|-----------|----------|-------|-------------------|
| traffic_density | min - 1 | -1 | Raises `ValueError` |
| traffic_density | max + 1 | 101 (150 used in test) | Raises `ValueError` |
| slope_angle | min - 1 | -11 | Raises `ValueError` |
| slope_angle | max + 1 | 11 (20 used in test) | Raises `ValueError` |

---

## Step 4 — Test case spreadsheet

`test_cases.csv` holds the nominal test configurations (one varied
parameter per row against the valid baseline). Expected outcomes were
computed from the requirements. The README's illustrative table rows
(e.g. `60 / true / clear / 12 / -2 / 62`) are inconsistent with the
safety-mode rule and were **not** copied.

---

## Step 5 — White-Box Test Design

Control-flow analysis of `update_speed()` yields the following tests in
`test_white_box.py`, chosen to execute every statement at least once.

| Test | Path / Statements Exercised | Reason Needed |
|------|-----------------------------|---------------|
| test_invalid_traffic_density_raises | traffic-density range check -> `raise ValueError` | Covers the traffic validation raise |
| test_invalid_slope_angle_raises | slope-angle range check -> `raise ValueError` | Covers the slope validation raise |
| test_invalid_road_condition_raises | road `else` branch -> `raise ValueError` | Covers the invalid-road raise |
| test_wet_high_traffic_uphill_safety_off | `wet` factor, `traffic > 80` (-20), `slope > 0`, safety-off `max()` | Covers wet branch, the -20 traffic branch, uphill branch, and the else (max) clamp |
| test_icy_mid_traffic_downhill_safety_on | `set_safety_mode`, `icy` factor, `50 <= traffic <= 80` (-10), `slope < 0`, safety-on `min()` | Covers icy branch, the -10 traffic branch, downhill branch, and the safety (min) clamp |
| test_clear_low_traffic_flat_safety_off | `clear` factor, `traffic < 50`, `slope == 0`, safety-off `max()` | Covers the clear branch and the no-adjustment paths |

---

## Step 6 — Measure Test Coverage

`coverage run -m unittest test_white_box.py` then `coverage report -m`
reports **100% statement coverage** on `speed_controller.py` (full output
in `coverage_results.txt`):

```
Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
speed_controller.py      35      0   100%
```

No `# pragma: no cover`, no removed logic, and no faked configuration
were used to reach 100%.

---

## Bugs Found

### What bugs did you find? (Step 4)

The inline `# Bug N` comments in the starter code are misleading: the
values they flag (`wet` = 0.85, the `traffic_density >= 50` boundary,
the slope direction, and the safety clamp) all match the written
requirements, so none of those were changed. The one genuine defect
surfaced by the black-box work is:

- **Missing range validation.** The requirements state that a
  `ValueError` must be raised when `traffic_density` is outside 0–100 or
  `slope_angle` is outside -10..+10 ("Error Handling"), but the original
  `update_speed()` validated only `road_condition`. Out-of-range numeric
  inputs were silently accepted and produced a numeric result instead of
  an error.
  - **Requirement:** "If any input parameter is outside its valid range
    ... the system shall raise a `ValueError`."
  - **Observed (before fix):** `update_speed('clear', 150, 0)` returned
    `40.0`; `update_speed('clear', 20, 20)` returned `40.0`.
  - **Test:** `test_invalid_traffic_density_raises`,
    `test_invalid_slope_angle_raises` (white-box).
  - **Cause:** No bounds checks on `traffic_density` or `slope_angle`.
  - **Fix (smallest change):** two guard clauses at the top of
    `update_speed()` raising `ValueError` for out-of-range values. The
    valid-input logic is unchanged, so every nominal expected value is
    unaffected.
  - **Verification:** both tests pass; the full suite of 16 tests passes.

The misleading `# Bug` comments were also removed so the source reflects
the actual (correct) behaviour.

### Did you find any more bugs? (Step 5)

No additional implementation defects were identified by the completed
white-box test set. At 100% statement coverage every branch of
`update_speed()` behaves as the requirements specify.
