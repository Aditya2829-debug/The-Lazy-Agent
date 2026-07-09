# LeetCode & GitHub Streak Keeper Bot 🚀

Yeh bot aapki day-to-day problem ko solve karta hai jisme aap local execution ya scheduled task ke through LeetCode par ek previously solved question resubmit kar sakte hain aur local GitHub README update karke automatically push kar sakte hain. Isse bina time nikale bhi aapki **LeetCode aur GitHub ki streak** continuous bani rahegi!

---

## Features
- **LeetCode Auto-Resubmit:** Aapke account ke dynamic accepted submissions ki list se ek random question fetch karke automatic submit karta hai. Agar koi accepted list nahi milti, toh default *Two Sum* logic submit karta hai.
- **GitHub Auto-Commit:** Streak status ko is repo ke `README.md` mein append karta hai aur commit karke push karta hai.
- **Windows Task Scheduler Integration:** Bina kisi external library ke directly windows scheduler task register kar deta hai jo daily scheduled time par chalega.
- **Cookie Security:** `.gitignore` configured hai taaki aapka private `config.json` file kabhi public GitHub repo par leak na ho.

---

## Setup Instructions

### 1. Requirements
Aapke system par **Python 3** aur **Git** installed hona chahiye:
- Python Version check karne ke liye: `python --version`
- Git Version check karne ke liye: `git --version`

### 2. LeetCode Cookies Kaise Extract Karein?
Bot ko authenticate karne ke liye aapko `LEETCODE_SESSION` aur `csrftoken` cookies ki jarurat padegi. Iske liye follow karein:
1. Apne web browser (Chrome/Edge/Firefox) par **[LeetCode](https://leetcode.com/)** par log in karein.
2. Web page par right-click karein aur **Inspect** select karein (ya keyboard par `F12` press karein).
3. **Application** tab (Chrome/Edge) ya **Storage** tab (Firefox) par jayein.
4. Left sidebar mein **Cookies** drop-down expand karke `https://leetcode.com` select karein.
5. List mein se in dono keys ki values copy karein:
   - `LEETCODE_SESSION`
   - `csrftoken`

### 3. Configuration
1. Apne folder mein `config.json` file ko open karein.
2. Usme cookies paste karein:
```json
{
  "leetcode": {
    "enabled": true,
    "leetcode_session": "PASTE_YOUR_LEETCODE_SESSION_HERE",
    "csrf_token": "PASTE_YOUR_CSRFTOKEN_HERE"
  },
  "github": {
    "enabled": true,
    "repo_path": ".",
    "branch": "main"
  }
}
```

---

## How to Use (Commands)

### A. Connection Test Karein
Sabse pehle connection confirm karne ke liye commands run karein:
- **LeetCode connection test:**
  ```bash
  python streak_keeper.py --test-leetcode
  ```
  *(Output successfully user status dikhayega, jaise: `[SUCCESS] Connected to LeetCode as user: username`)*

- **GitHub connection test:**
  ```bash
  python streak_keeper.py --test-github
  ```

---

### B. Manually Run Karein (Streak Maintain)
Streak manually chalane ke liye:
```bash
python streak_keeper.py --run
```
Yeh command run hote hi:
1. LeetCode se ek random solve kiya question fetch karke resubmit karegi.
2. Submission evaluation check karegi.
3. README update karke commit aur push karegi.

---

### C. Automatic Daily Schedule Setup Karein
Agar aap chahte hain ki yeh bot daily background mein specific time par run kare:
```bash
python streak_keeper.py --schedule HH:MM
```
**Example (Raat ko 9:30 baje run karne ke liye):**
```bash
python streak_keeper.py --schedule 21:30
```
Isse Windows Task Scheduler mein `LeetCodeGitHubStreakKeeper` task create ho jayega jo background mein automated process trigger karega.

---

### D. Daily Schedule Remove Karein
Schedule delete karne ke liye:
```bash
python streak_keeper.py --unschedule
```

---

## Streak Log

*(Yahan par bot auto-resubmission updates register karega)*
* 2026-06-25 22:17:50 Local Time - Resubmitted LeetCode problem: [Two Sum](https://leetcode.com/problems/two-sum/)
* 2026-06-25 22:23:22 Local Time - Resubmitted LeetCode problem: [Create Target Array in the Given Order](https://leetcode.com/problems/create-target-array-in-the-given-order/)
* 2026-06-25 22:30:39 Local Time - Resubmitted LeetCode problem: [Two Sum](https://leetcode.com/problems/two-sum/)
* 2026-06-25 22:35:29 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-06-26 14:22:33 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-06-26 22:00:14 Local Time - Resubmitted LeetCode problem: [Create Target Array in the Given Order](https://leetcode.com/problems/create-target-array-in-the-given-order/)
* 2026-06-27 16:30:47 Local Time - Resubmitted LeetCode problem: [Generic Commit](https://leetcode.com/problems/git-commit/)
* 2026-06-27 16:38:00 Local Time - Resubmitted LeetCode problem: [Create Target Array in the Given Order](https://leetcode.com/problems/create-target-array-in-the-given-order/)
* 2026-06-27 22:32:19 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-06-28 16:11:06 Local Time - Resubmitted LeetCode problem: [Create Target Array in the Given Order](https://leetcode.com/problems/create-target-array-in-the-given-order/)
* 2026-06-28 22:00:14 Local Time - Resubmitted LeetCode problem: [Create Target Array in the Given Order](https://leetcode.com/problems/create-target-array-in-the-given-order/)
* 2026-06-29 14:00:14 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-06-29 15:44:13 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-06-29 22:00:14 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-06-30 15:44:12 Local Time - Resubmitted LeetCode problem: [Two Sum](https://leetcode.com/problems/two-sum/)
* 2026-06-30 22:00:12 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-02 15:44:13 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-03 14:00:13 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-07-03 15:44:12 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-03 23:45:27 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-04 15:44:12 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-04 22:00:13 Local Time - Resubmitted LeetCode problem: [Two Sum](https://leetcode.com/problems/two-sum/)
* 2026-07-05 15:44:12 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-05 17:35:21 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-07-05 22:00:14 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-07-06 14:00:12 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-07-06 15:44:12 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-07 01:12:17 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-07 15:44:12 Local Time - Resubmitted LeetCode problem: [Two Sum](https://leetcode.com/problems/two-sum/)
* 2026-07-08 00:02:27 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-08 14:00:17 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-07-08 15:44:15 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
* 2026-07-08 22:00:13 Local Time - Resubmitted LeetCode problem: [Missing Number](https://leetcode.com/problems/missing-number/)
* 2026-07-09 15:31:45 Local Time - Resubmitted LeetCode problem: [Shuffle the Array](https://leetcode.com/problems/shuffle-the-array/)
