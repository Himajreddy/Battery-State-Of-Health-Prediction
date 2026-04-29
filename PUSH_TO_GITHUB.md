# Pushing this project to GitHub

A concrete checklist. Do these in order.

## 1. Configure git (one-time, skip if already done)

```bash
git config --global user.name  "Your Name"
git config --global user.email "your.email@example.com"
```

The email must match the one you've verified on GitHub, otherwise the
commits won't be linked to your profile.

## 2. Customise the placeholders

These three files have `[YOUR NAME]` or similar placeholders. Open them
in any editor and replace the bracketed text with your real details.
Search the project for `[YOUR ` to find them all in one go:

```bash
grep -rn "\[YOUR " .
```

Files that need editing:

- **LICENSE** — change `[YOUR NAME]` in the copyright line.
- **README.md** — fill in the "About me" section at the bottom (your
  name, your university/year, optionally a link to your homepage or
  LinkedIn).
- **docs/report_template.md** — only matters once you start writing the
  report (Week 4); leave for later.

## 3. Initialise the local git repo with a clean commit history

```bash
bash setup_git.sh
```

This creates ten logical commits instead of one giant "initial commit".
A reviewer skimming your commit graph will see the project came together
in steps, which is what real work looks like.

If the script complains about `user.name` not being set, go back to
step 1.

## 4. Create the empty repo on GitHub

Go to https://github.com/new and:

- **Repository name:** `battery-soh-prediction` (lowercase, hyphens, no
  marketing words).
- **Description:** *Predicting Li-ion battery State of Health from
  cycle-level features — feature ablation study on the NASA PCoE dataset.*
- **Visibility:** Public.
- **Do NOT** check "Add a README", "Add .gitignore", or "Choose a
  license". You already have all three locally.

Click **Create repository**.

## 5. Connect and push

GitHub will show you a snippet labelled "…push an existing repository
from the command line". It looks like this (replace `YOUR_USERNAME`):

```bash
git remote add origin git@github.com:YOUR_USERNAME/battery-soh-prediction.git
git branch -M main
git push -u origin main
```

If you've never set up SSH keys for GitHub, use the HTTPS form instead:

```bash
git remote add origin https://github.com/YOUR_USERNAME/battery-soh-prediction.git
git branch -M main
git push -u origin main
```

GitHub will ask for your username and a personal-access token (not your
password). Generate one at https://github.com/settings/tokens if needed.

## 6. Polish the GitHub page (5 minutes, big payoff)

These details matter to reviewers and take very little time:

- **Edit the "About" sidebar** on the repo page. Click the gear icon
  next to "About". Re-paste the description from step 4. Add topics:
  `machine-learning`, `random-forest`, `xgboost`, `battery`,
  `prognostics`, `nasa-dataset`, `feature-engineering`. Topics are how
  reviewers (and recruiters later) get context in five seconds.
- **Pin the repo** on your profile. Go to your profile page, click
  "Customize your pins", check this repo. If it's one of your only ML
  projects, the pinned slot does serious work.
- **Profile README.** If you don't have a `YOUR_USERNAME/YOUR_USERNAME`
  repo with a profile README, create one. Three short lines about who
  you are. An empty profile undersells the project a reviewer just
  arrived at.

## 7. Verify it works from a clean clone

This is the one step most students skip and it's the most important. In
a different folder:

```bash
git clone https://github.com/YOUR_USERNAME/battery-soh-prediction.git verify
cd verify
pip install -r requirements.txt
# Drop the four NASA .mat files into data/raw/ then:
python scripts/load_data.py
python scripts/ablation.py
```

If anything breaks (missing import, hardcoded path, typo), fix it,
commit, push, and verify again. A reviewer who hits the same wall on
your repo will form an unflattering opinion in about ten seconds.

## After you have results

Once you've run the ablation on real data and written the report:

```bash
# Add the final report PDF
git add docs/report.pdf
git commit -m "Add final report"

# Update README with the results table (replace the TBD placeholders)
git add README.md
git commit -m "Add ablation results to README"

git push
```

That last commit — README updated with real numbers — is what makes the
repo look finished.
