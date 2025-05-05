import requests
import concurrent.futures
import time
from bs4 import BeautifulSoup
import random
import matplotlib.pyplot as plt
import psycopg2

HOME_URL = "https://nmustafa.scripts.mit.edu/seniorweek25"
SUBMIT_URL = HOME_URL + "/lottery/submit/"

NUM_USERS = 100

def get_events():
    conn = psycopg2.connect(
        host="XXX",
        database="XXX",
        user="XXX",
        password="XXX"
    )
    cur = conn.cursor()

    cur.execute("SELECT name FROM events")
    events = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return events

EVENTS = get_events()
print(EVENTS)

def submit_form(user_id):
    try:
        session = requests.Session()

        # Time loading home screen
        home_request_start = time.time()
        response = session.get(HOME_URL)
        home_request_end = time.time()
        debug_print(f"[User {user_id}] Got home screen")

        if response.status_code != 200:
            print(f"[User {user_id}] Failed to load home page")
            return

        # Need to get CSFR token for django
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if not csrf_token:
            print(f"[User {user_id}] No CSRF token found")
            return

        csrf_token_value = csrf_token["value"]

        selection_time = random.randint(1, 5)
        debug_print(f"[User {user_id}] Sleeping for {selection_time}s")
        time.sleep(selection_time)


        # Randomly choose some events and values
        form_data = {
            "csrfmiddlewaretoken": csrf_token_value
        }
        num_events = random.randint(2, 6) 
        selected_events = random.sample(EVENTS, num_events)
        total_points = 0
        for event in selected_events:
            points = random.randint(1, 500)
            total_points += points
            form_data[event] = points
        debug_print(f"[User {user_id}] Submitting events with {total_points} total points: {form_data}")

        # Submit the form
        headers = {
            "Referer": HOME_URL # CSRF protection requires this
        }
        submit_request_start = time.time()
        post_response = session.post(SUBMIT_URL, data=form_data, headers=headers)
        submit_request_end = time.time()
        debug_print(f"[User {user_id}] Submitted: Status {post_response.status_code}")
        if "Successfully submitted" in str(post_response.content):
            if total_points > 1000:
                print(f"[User {user_id}] ERROR: ACCEPTED WHEN SHOULD'VE REJECTED")
                print(f"[User {user_id}] events: {form_data} total points: {total_points}")
                print(f"[User {user_id}] response: {str(post_response.content)}")
        else:
            if total_points <= 1000:
                print(f"[User {user_id}] ERROR: REJECTED WHEN SHOULD'VE ACCEPTED")
                print(f"[User {user_id}] events: {form_data} total points: {total_points}")
                print(f"[User {user_id}] response: {str(post_response.content)}")


        home_request_duration = home_request_end - home_request_start
        submit_form_duration = submit_request_end - submit_request_start
        total_duration = home_request_duration + submit_form_duration
        print(f"[User {user_id}] Loading home screen took {home_request_duration:.2f}s, submitting form took {submit_form_duration:.2f}s, for a total of {total_duration:.2f}s")
        return user_id, home_request_duration, submit_form_duration

    except Exception as e:
        print(f"[User {user_id}] Error: {e}")


def plot_load_times(results):

    home_durations = [r[0] for r in results]
    submit_durations = [r[1] for r in results]
    total_durations = [h + s for h, s in results]

    x = list(range(len(results)))  # Index for each valid user

    avg_home = sum(home_durations) / len(home_durations)
    avg_submit = sum(submit_durations) / len(submit_durations)
    avg_total = sum(total_durations) / len(total_durations)

    plt.figure(figsize=(12, 6))
    plt.plot(x, home_durations, label='Home Load Time', marker='o')
    plt.plot(x, submit_durations, label='Submit Load Time', marker='s')
    plt.plot(x, total_durations, label='Total Load Time', marker='^')

    plt.axhline(avg_home, color='blue', linestyle='--', linewidth=1, label=f'Avg Home ({avg_home:.2f}s)')
    plt.axhline(avg_submit, color='orange', linestyle='--', linewidth=1, label=f'Avg Submit ({avg_submit:.2f}s)')
    plt.axhline(avg_total, color='green', linestyle='--', linewidth=1, label=f'Avg Total ({avg_total:.2f}s)')

    plt.xlabel("Completion Order")
    plt.ylabel("Duration (seconds)")
    plt.title("Page Load Durations per User")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


DEBUG = False
def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def load_test():
    results = []

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        futures = [
            executor.submit(submit_form, i)
            for i in range(NUM_USERS)
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if not result:
                continue
            user_id, home_duration, submit_duration = result
            results.append((home_duration, submit_duration))
    duration = time.time() - start_time
    print(f"\nCompleted {NUM_USERS} requests in {duration:.2f} seconds")

    plot_load_times(results)

if __name__ == "__main__": 
    load_test()
