# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Purpose:** The game is a number-guessing challenge in which the player chooses a difficulty, enters whole-number guesses, receives Higher/Lower feedback, manages an attempt limit, and tries to earn the best score.
- [x] **Bugs found:** The starter hinted in the wrong direction, decimal input could be silently truncated, difficulty changes could leave a secret outside the selected range, and the first-win score formula was incorrect.
- [x] **Fixes applied:** The core guessing and scoring functions were moved into `logic_utils.py`, the `Too High`/`Too Low` outcomes and hints were corrected, difficulty changes now reset session state and generate a secret in the new range, and decimal input is rejected instead of truncated.

## Demo Walkthrough

1. Select **Normal** difficulty. The game displays a range of 1 to 100 and allows 8 attempts.
2. Open **Developer Debug Info** and note the generated secret; for this example, assume it is 50.
3. Enter a guess of **60** and submit. The game decrements attempts and shows the outcome `Too High` with `📉 Go LOWER!`.
4. Enter a guess of **40** and submit. The game shows `Too Low` with `📈 Go HIGHER!`; a wrong guess decreases the score by 5 points.
5. Enter **50** and submit. The game displays `🎉 Correct!`, awards points for the winning attempt, shows balloons, and presents the final score.
6. Click **New Game** to clear the attempts, score, history, and old secret, then generate a fresh secret for the selected difficulty.

## 🧪 Test Results

```text
$ python3 -m pytest -q
....                                                                     [100%]
4 passed in 0.00s
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
