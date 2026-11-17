# Screenshot Guide — commands to run for submission evidence

Run these from the `unit-testing/` directory with the virtual
environment active (`coverage` from `requirements.txt` must be
installed). Capture a screenshot of each command and its output.

```bash
# 1. Install dependencies (once)
pip install -r requirements.txt

# 2. Black-box tests — 10 tests, all pass
python -m unittest test_black_box.py -v

# 3. White-box tests — 6 tests, all pass
python -m unittest test_white_box.py -v

# 4. Full suite — 16 tests, all pass
python -m unittest -v

# 5. Coverage — 100% on speed_controller.py
coverage erase
coverage run -m unittest test_white_box.py
coverage report -m
```

### Expected results

- Step 2: `Ran 10 tests ... OK`
- Step 3: `Ran 6 tests ... OK`
- Step 4: `Ran 16 tests ... OK`
- Step 5: `speed_controller.py   35   0   100%`

A saved copy of the coverage report is in `coverage_results.txt`.
