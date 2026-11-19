# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The game opened with a title, difficulty sidebar, developer debug information, guess form, and score controls. I completed two playthrough-style simulations with different inputs. In the first, I checked a decimal guess and an ordinary out-of-range value; in the second, I changed difficulty and tested first-win scoring. The main visible/code-level issues were decimal input being silently truncated, a secret that could remain outside a newly selected difficulty range, and an incorrect first-win score calculation. I also ran the project tests and found that the extracted `logic_utils.py` functions had not been implemented.

**Bug Reproduction Logs**

| Input / Trigger | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|---|---|---|---|
| Enter `60.9` with secret `50` | The input should be rejected as not a whole-number guess | `parse_guess` used `int(float(raw))`, so it silently accepted the input as integer `60` and returned a "Too High / Go LOWER" result | none in the app log | `app.py`, `parse_guess` |
| Start on Normal (`1–100`) with secret `50`, then switch to Easy (`1–20`) | Switching difficulty should generate or preserve a secret inside the Easy range | The existing secret remained `50`, outside `1–20`, so every valid Easy guess was too low and winning was impossible until a new game/reset | No console error; Developer Debug Info showed the out-of-range secret | `app.py`, difficulty state initialization and change handling around `difficulty`, `low`, `high`, and `st.session_state.secret` |
| Win on the first attempt | The first win should receive the full first-attempt reward (the UI does not define an exact reward, but a 100-point baseline is the apparent intent) | `update_score(0, "Win", 1)` awarded 80 points because it calculates `100 - 10 * (attempt_number + 1)` | none | `app.py`, `update_score`, especially the `attempt_number + 1` expression |
| Run `pytest tests/test_game_logic.py -q` | The extracted logic module should provide working get-range, parsing, guess, and score functions | All 3 current guess tests fail with `NotImplementedError` from `logic_utils.py` | `3 failed: ... NotImplementedError: Refactor this function from app.py into logic_utils.py` | `logic_utils.py`, `check_guess` and its other stubbed functions |

---

## 2. How did you use AI as a teammate?

I used GitHub Copilot in VS Code as an implementation and verification teammate. One correct suggestion was to move `check_guess`, `parse_guess`, `get_range_for_difficulty`, and `update_score` into `logic_utils.py` and import them in `app.py`. This was correct because it separated UI reruns and session-state work from reusable rules and gave the tests a module without UI dependencies. I verified it by adding the `60` versus `50` regression test and seeing the complete suite pass with 4 tests.

I did not accept the first fix for decimal input as written because the suggestion used `int(float(raw))`, which would silently turn `60.9` into `60`. I changed it to `int(raw)` in `parse_guess`, so decimal text is rejected with `"That is not a whole number."` instead of being truncated. I verified this by inspecting `parse_guess("60.9")` and confirming that it returned `ok=False` rather than a numeric guess.

## 3. Debugging and testing your fixes

I decided that a bug was fixed only after reproducing the original bad behavior, changing the producer of the behavior, and running a focused test. The key pytest regression uses `check_guess(60, 50)` and verifies both the `"Too High"` outcome and `"📉 Go LOWER!"` hint. I also ran the full suite; it changed from 3 failing tests to 4 passing tests, including the new specific regression case. In addition, I compiled both Python files and confirmed the Streamlit app responded successfully at `http://localhost:8501`.

AI helped me understand that Streamlit reruns the script and that the UI-visible hint must call the shared `check_guess` function rather than duplicate logic in `app.py`. I used that relationship to verify the import and call at `app.py` and the implementation in `logic_utils.py`.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns the Python script from the top whenever the user interacts with an input, button, checkbox, or sidebar control. Because ordinary local variables are recreated during each rerun, values that must survive between interactions belong in `st.session_state`. In this project, session state kept the secret, attempts, score, status, and history stable until an action such as **New Game** or a difficulty change intentionally reset them.

---

## 5. Looking ahead: your developer habits

I want to reuse focused regression tests and a reproduce-fix-verify workflow in future projects. The test for `check_guess(60, 50)` gave immediate evidence that the hint bug was corrected while also protecting that behavior from later regressions.

Next time, I would compare AI-generated changes with the actual codebase before applying them and ask for a test-driven patch earlier. This experience changed how I think about AI-generated code: it can produce useful structure quickly, but it is still a draft that must be reviewed, traced to the UI, and verified with tests or runtime evidence.
