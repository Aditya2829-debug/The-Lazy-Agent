import os
import sys
import json
import random
import time
import subprocess
import requests

# ANSI colors for premium console experience
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Dynamic directories relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

# Bulletproof fallback solution in case LeetCode fetch fails
FALLBACK_PROBLEM = {
    "title": "Two Sum",
    "titleSlug": "two-sum",
    "questionId": "1",
    "lang": "python3",
    "code": """class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        lookup = {}
        for i, num in enumerate(nums):
            if target - num in lookup:
                return [lookup[target - num], i]
            lookup[num] = i
        return []
"""
}

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {Colors.BOLD}{msg}{Colors.END}")

def log_warn(msg):
    print(f"{Colors.WARNING}[WARNING]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.FAIL}[ERROR]{Colors.END} {Colors.BOLD}{msg}{Colors.END}")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        log_error("config.json not found! Please create it from config.json.template.")
        sys.exit(1)
    
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to parse config.json: {e}")
        sys.exit(1)

def run_git_command(args, cwd):
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log_error(f"Git command failed: {' '.join(args)}")
        log_error(f"Stdout: {e.stdout}")
        log_error(f"Stderr: {e.stderr}")
        raise e

# --- LEETCODE AUTOMATION SECTION ---

def make_graphql_request(query, variables, cookies):
    url = "https://leetcode.com/graphql/"
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/",
        "x-csrftoken": cookies.get("csrftoken", ""),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers, cookies=cookies, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(f"GraphQL request returned status code {response.status_code}")
            return None
    except Exception as e:
        log_error(f"Network error during GraphQL request: {e}")
        return None

def test_leetcode_connection(leetcode_session, csrf_token):
    cookies = {"LEETCODE_SESSION": leetcode_session, "csrftoken": csrf_token}
    query = """
    query globalData {
      userStatus {
        username
        isSignedIn
      }
    }
    """
    data = make_graphql_request(query, {}, cookies)
    if data and "data" in data and "userStatus" in data["data"]:
        status = data["data"]["userStatus"]
        if status.get("isSignedIn"):
            log_success(f"Connected to LeetCode as user: {status.get('username')}")
            return status.get("username")
        else:
            log_error("LeetCode connection test failed. Cookies are invalid or expired (user is not signed in).")
    else:
        log_error("Failed to connect to LeetCode GraphQL API.")
    return None

def get_recent_accepted_submissions(username, cookies):
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
      recentAcSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
      }
    }
    """
    data = make_graphql_request(query, {"username": username, "limit": 10}, cookies)
    if data and "data" in data and "recentAcSubmissionList" in data["data"]:
        return data["data"]["recentAcSubmissionList"]
    return []

def get_submission_code(submission_id, cookies):
    query = """
    query submissionDetails($submissionId: Int!) {
      submissionDetails(submissionId: $submissionId) {
        code
        lang
        question {
          questionId
          titleSlug
        }
      }
    }
    """
    data = make_graphql_request(query, {"submissionId": int(submission_id)}, cookies)
    if data and "data" in data and "submissionDetails" in data["data"]:
        details = data["data"]["submissionDetails"]
        if details:
            return details
    return None

def get_question_id(title_slug, cookies):
    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
      }
    }
    """
    data = make_graphql_request(query, {"titleSlug": title_slug}, cookies)
    if data and "data" in data and "question" in data["data"] and data["data"]["question"]:
        return data["data"]["question"]["questionId"]
    return None

def submit_solution(title_slug, question_id, lang, code, cookies):
    url = f"https://leetcode.com/problems/{title_slug}/submit/"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/problems/{title_slug}/",
        "x-csrftoken": cookies.get("csrftoken", ""),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {
        "lang": lang,
        "question_id": str(question_id),
        "typed_code": code
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=15)
        if response.status_code == 200:
            return response.json().get("submission_id")
        else:
            log_error(f"Solution submission failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_error(f"Network error during solution submission: {e}")
        return None

def poll_submission_status(title_slug, submission_id, cookies):
    url = f"https://leetcode.com/submissions/detail/{submission_id}/check/"
    headers = {
        "Referer": f"https://leetcode.com/problems/{title_slug}/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    log_info("Polling submission status...")
    for _ in range(6):
        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            if response.status_code == 200:
                result = response.json()
                state = result.get("state")
                if state == "SUCCESS":
                    status = result.get("status_msg")
                    if status == "Accepted":
                        log_success(f"LeetCode Submission Accepted! (Runtime: {result.get('status_runtime')}, Memory: {result.get('status_memory')})")
                        return True
                    else:
                        log_warn(f"Submission finished but status was: {status}")
                        return True
                elif state in ["PENDING", "STARTED"]:
                    time.sleep(2)
                else:
                    log_warn(f"Unknown submission state: {state}")
                    return False
            else:
                log_error(f"Polling returned status code {response.status_code}")
                time.sleep(2)
        except Exception as e:
            log_error(f"Error while polling: {e}")
            time.sleep(2)
    
    log_warn("Polling timed out. The submission is still processing, but it should count towards your streak.")
    return True

# --- GITHUB AUTOMATION SECTION ---

def check_github_repo(repo_path):
    # Resolve relative path if '.' is provided
    abs_repo_path = os.path.abspath(os.path.join(SCRIPT_DIR, repo_path))
    if not os.path.exists(abs_repo_path):
        log_error(f"GitHub repository path does not exist: {abs_repo_path}")
        return False
    
    try:
        # Check if inside git directory
        run_git_command(["git", "rev-parse", "--is-inside-work-tree"], abs_repo_path)
        # Check current status
        status = run_git_command(["git", "status", "--short"], abs_repo_path)
        log_success(f"Verified Git repository at: {abs_repo_path}")
        if status:
            log_info(f"Uncommitted changes in repository:\n{status}")
        else:
            log_info("Git repository is clean.")
        return True
    except Exception as e:
        log_error(f"Directory is not a valid Git repository: {abs_repo_path}")
        return False

def commit_and_push_streak(repo_path, branch, problem_title, problem_slug):
    abs_repo_path = os.path.abspath(os.path.join(SCRIPT_DIR, repo_path))
    readme_path = os.path.join(abs_repo_path, "README.md")
    
    log_info("Updating README.md with the latest streak log...")
    
    # 1. Update README.md
    log_line = f"\n* {time.strftime('%Y-%m-%d %H:%M:%S Local Time')} - Resubmitted LeetCode problem: [{problem_title}](https://leetcode.com/problems/{problem_slug}/)"
    
    try:
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "# The Lazy Agent's Streak Log\n\nDaily activity logs for maintaining LeetCode and GitHub streaks.\n"
        
        # Append the new log entry
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content.rstrip() + log_line + "\n")
            
        log_info("README.md updated locally.")
    except Exception as e:
        log_error(f"Failed to update README.md file: {e}")
        return False
    
    # 2. Commit and Push
    try:
        log_info("Running git add...")
        run_git_command(["git", "add", "README.md"], abs_repo_path)
        
        commit_message = f"Streak Update: Resubmitted LeetCode problem '{problem_title}'"
        log_info(f"Running git commit with message: '{commit_message}'...")
        run_git_command(["git", "commit", "-m", commit_message], abs_repo_path)
        
        log_info(f"Running git push origin {branch}...")
        run_git_command(["git", "push", "origin", branch], abs_repo_path)
        
        log_success("Streak committed and pushed to GitHub successfully!")
        return True
    except Exception as e:
        log_error("Failed to commit and push changes to GitHub.")
        return False

# --- SCHEDULER SECTION ---

def create_scheduler_task(time_str):
    script_path = os.path.abspath(__file__)
    python_exe = sys.executable
    task_name = "LeetCodeGitHubStreakKeeper"
    
    # Constructing a robust scheduled task command with double-quoted paths for Windows
    cmd = f'schtasks /create /tn "{task_name}" /tr "\\"{python_exe}\\" \\"{script_path}\\" --run" /sc daily /st {time_str} /f'
    
    log_info(f"Registering Windows Task Scheduler task '{task_name}' at {time_str} daily...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        log_success(f"Task scheduled successfully!\n{result.stdout.strip()}")
        log_info("You can verify it in Windows Task Scheduler or query it using:")
        print(f"  schtasks /query /tn \"{task_name}\"")
    except subprocess.CalledProcessError as e:
        log_error("Failed to register Windows scheduled task.")
        log_error(f"Stderr: {e.stderr.strip()}")
        log_info("Try running this shell command with administrator rights if needed.")

def remove_scheduler_task():
    task_name = "LeetCodeGitHubStreakKeeper"
    cmd = f'schtasks /delete /tn "{task_name}" /f'
    
    log_info(f"Deleting Windows Task Scheduler task '{task_name}'...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        log_success(f"Task removed successfully!\n{result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        log_warn("Failed to delete the task or it does not exist.")
        log_error(f"Stderr: {e.stderr.strip()}")

# --- MAIN RUNNER ---

def run_streak():
    config = load_config()
    
    leetcode_config = config.get("leetcode", {})
    github_config = config.get("github", {})
    
    problem_title = "Generic Commit"
    problem_slug = "git-commit"
    
    if leetcode_config.get("enabled"):
        log_info("--- LeetCode Streak Automation Start ---")
        session = leetcode_config.get("leetcode_session")
        csrf = leetcode_config.get("csrf_token")
        
        if not session or not csrf:
            log_error("LeetCode credentials are not set in config.json. Skipping LeetCode...")
        else:
            cookies = {"LEETCODE_SESSION": session, "csrftoken": csrf}
            username = test_leetcode_connection(session, csrf)
            
            selected_problem = None
            if username:
                log_info("Retrieving your recent accepted submissions...")
                submissions = get_recent_accepted_submissions(username, cookies)
                
                # Filter out valid ones and pick a random one
                valid_submissions = [s for s in submissions if s.get("id")]
                if valid_submissions:
                    # Choose a random solved problem to submit
                    random_sub = random.choice(valid_submissions)
                    log_info(f"Selected random solved problem: {random_sub['title']} (Slug: {random_sub['titleSlug']})")
                    
                    # Fetch submission detail code
                    detail = get_submission_code(random_sub["id"], cookies)
                    if detail:
                        # Fetch numeric question ID if not directly in submission details
                        question_info = detail.get("question", {})
                        question_id = question_info.get("questionId")
                        if not question_id:
                            question_id = get_question_id(random_sub["titleSlug"], cookies)
                            
                        if question_id:
                            selected_problem = {
                                "title": random_sub["title"],
                                "titleSlug": random_sub["titleSlug"],
                                "questionId": question_id,
                                "lang": detail.get("lang"),
                                "code": detail.get("code")
                            }
                        else:
                            log_warn(f"Could not retrieve questionId for slug {random_sub['titleSlug']}")
                    else:
                        log_warn(f"Could not retrieve code for submission ID {random_sub['id']}")
                else:
                    log_warn("No recent accepted submissions found on your account.")
            
            # Use fallback if unable to fetch one
            if not selected_problem:
                log_warn("Using fallback Two Sum solution to maintain the streak...")
                selected_problem = FALLBACK_PROBLEM
            
            # Submit the solution
            log_info(f"Submitting solution to '{selected_problem['title']}'...")
            sub_id = submit_solution(
                selected_problem["titleSlug"],
                selected_problem["questionId"],
                selected_problem["lang"],
                selected_problem["code"],
                cookies
            )
            
            if sub_id:
                log_success(f"Submission successful! ID: {sub_id}")
                poll_submission_status(selected_problem["titleSlug"], sub_id, cookies)
                problem_title = selected_problem["title"]
                problem_slug = selected_problem["titleSlug"]
            else:
                log_error("LeetCode code submission failed.")
    
    if github_config.get("enabled"):
        log_info("--- GitHub Streak Automation Start ---")
        repo_path = github_config.get("repo_path", ".")
        branch = github_config.get("branch", "main")
        
        if check_github_repo(repo_path):
            commit_and_push_streak(repo_path, branch, problem_title, problem_slug)
        else:
            log_error("Skipping Git update due to repository errors.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{Colors.HEADER}{Colors.BOLD}LeetCode & GitHub Streak Keeper{Colors.END}")
        print("Usage:")
        print("  python streak_keeper.py --run               - Run the automation once immediately")
        print("  python streak_keeper.py --test-leetcode     - Test LeetCode connection status")
        print("  python streak_keeper.py --test-github       - Check local Git repository status")
        print("  python streak_keeper.py --schedule HH:MM    - Register task in Windows Task Scheduler (e.g. 21:30)")
        print("  python streak_keeper.py --unschedule        - Unregister Windows task")
        sys.exit(0)
        
    cmd = sys.argv[1]
    
    if cmd == "--run":
        run_streak()
    elif cmd == "--test-leetcode":
        cfg = load_config()
        lc = cfg.get("leetcode", {})
        test_leetcode_connection(lc.get("leetcode_session"), lc.get("csrf_token"))
    elif cmd == "--test-github":
        cfg = load_config()
        gh = cfg.get("github", {})
        check_github_repo(gh.get("repo_path", "."))
    elif cmd == "--schedule":
        if len(sys.argv) < 3:
            log_error("Please specify scheduling time (e.g., --schedule 21:00)")
        else:
            create_scheduler_task(sys.argv[2])
    elif cmd == "--unschedule":
        remove_scheduler_task()
    else:
        log_error(f"Unknown argument: {cmd}")
