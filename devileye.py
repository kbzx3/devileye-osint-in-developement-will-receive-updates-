import requests
import itertools
import Levenshtein
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

def generate_similar_usernames(username):
    similar_usernames = set()
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789_'

    # Change one character
    for i in range(len(username)):
        for c in alphabet:
            if username[i] != c:
                similar_usernames.add(username[:i] + c + username[i+1:])
    
    # Add one character
    for i in range(len(username) + 1):
        for c in alphabet:
            similar_usernames.add(username[:i] + c + username[i:])
    
    # Remove one character
    for i in range(len(username)):
        similar_usernames.add(username[:i] + username[i+1:])
    
    # Add underscores
    for i in range(len(username) + 1):
        similar_usernames.add(username[:i] + '_' + username[i:])
    
    # Substrings
    for i in range(len(username)):
        for j in range(i + 1, len(username) + 1):
            similar_usernames.add(username[i:j])
    
    # Permutations
    for perm in itertools.permutations(username):
        similar_usernames.add(''.join(perm))
    
    return similar_usernames

def get_user_details(platform, username):
    try:
        if platform == 'github':
            url = f'https://github.com/{username}'
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                details = {
                    'username': username,
                    'name': soup.find('span', class_='p-name').text.strip() if soup.find('span', class_='p-name') else 'N/A',
                    'bio': soup.find('div', class_='p-note').text.strip() if soup.find('div', class_='p-note') else 'N/A',
                    'public_repos': soup.find('a', href=f'/{username}?tab=repositories').text.strip() if soup.find('a', href=f'/{username}?tab=repositories') else 'N/A',
                    'followers': soup.find('a', href=f'/{username}?tab=followers').text.strip() if soup.find('a', href=f'/{username}?tab=followers') else 'N/A',
                    'following': soup.find('a', href=f'/{username}?tab=following').text.strip() if soup.find('a', href=f'/{username}?tab=following') else 'N/A',
                }
                return details
            else:
                print(f"GitHub profile for {username} not found.")
                return None

        elif platform == 'twitter':
            url = f'https://twitter.com/{username}'
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                details = {
                    'username': username,
                    'name': soup.find('div', class_='css-1dbjc4n').find('span').text.strip() if soup.find('div', class_='css-1dbjc4n') else 'N/A',
                    'bio': soup.find('div', class_='css-901oao').text.strip() if soup.find('div', class_='css-901oao') else 'N/A',
                    'location': soup.find('div', class_='css-1dbjc4n').find_all('span')[1].text.strip() if soup.find('div', class_='css-1dbjc4n') and len(soup.find('div', class_='css-1dbjc4n').find_all('span')) > 1 else 'N/A',
                }
                return details
            else:
                print(f"Twitter profile for {username} not found.")
                return None

        elif platform == 'facebook':
            url = f'https://www.facebook.com/{username}'
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                details = {
                    'username': username,
                    'name': soup.find('title').text.strip() if soup.find('title') else 'N/A',
                }
                return details
            else:
                print(f"Facebook profile for {username} not found.")
                return None

        elif platform == 'instagram':
            url = f'https://www.instagram.com/{username}/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                details = {}
                
                meta_description = soup.find('meta', property='og:description')
                if meta_description:
                    content = meta_description.get('content', '')
                    parts = content.split(' ')
                    if len(parts) >= 4:
                        details['name'] = parts[0]
                        details['followers'] = parts[2]
                        details['following'] = parts[4]
                        details['posts'] = parts[6]

                meta_image = soup.find('meta', property='og:image')
                if meta_image:
                    details['profile_picture'] = meta_image.get('content', '')

                return details
            else:
                print(f"Instagram profile for {username} not found.")
                return None
    except Exception as e:
        print(f"Error fetching details from {platform}: {e}")
        return None

def check_username(username):
    sites = {
        "YouTube": f"https://www.youtube.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}",
        "Facebook": f"https://www.facebook.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "GitHub": f"https://github.com/{username}"
    }   

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    found_sites = []

    for site, url in sites.items():
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                found_sites.append((site, url))
                print(f"Username found on {site}: {url}")
            else:
                print(f"Username not found on {site}")
        except requests.RequestException as e:
            print(f"Could not connect to {site}: {e}")

    return found_sites

def username_finder():
    username = input("Enter a username to search for: ")
    print(f"Searching for username: {username}")
    found_sites = check_username(username)
    
    similar_usernames = generate_similar_usernames(username)
    all_found_sites = set(found_sites)
    
    for similar_username in similar_usernames:
        if Levenshtein.distance(username, similar_username) <= 2:
            print(f"Checking similar username: {similar_username}")
            similar_found_sites = check_username(similar_username)
            all_found_sites.update(similar_found_sites)

    if all_found_sites:
        print(f"\n\nFound the following profiles for '{username}' and similar usernames:")
        for site, url in all_found_sites:
            print(f"Username found on {site}: {url}")
    else:
        print(f"\n\nNo profiles found for '{username}' or similar usernames.")

def account_details_fetcher():
    username = input("Enter a username to fetch details for: ")
    print(f"Fetching details for username: {username}")
    platforms = ['github', 'twitter', 'facebook', 'instagram']
    
    for platform in platforms:
        details = get_user_details(platform, username)
        if details:
            print(f"\nDetails for '{username}' on {platform.capitalize()}:")
            for key, value in details.items():
                print(f"{key}: {value}")
        else:
            print(f"\nNo details found for '{username}' on {platform.capitalize()}.")

def get_phone_details(phone_number, country_code):
    details = {}
    
    try:
        phone_number_obj = phonenumbers.parse(phone_number, country_code)
        
        if not phonenumbers.is_valid_number(phone_number_obj):
            return {"error": "Invalid phone number"}
        
        details['location'] = geocoder.description_for_number(phone_number_obj, 'en')
        details['carrier'] = carrier.name_for_number(phone_number_obj, 'en')
        details['timezone'] = timezone.time_zones_for_number(phone_number_obj)
        
    except phonenumbers.NumberParseException:
        details['error'] = "Number parse exception occurred"
    
    return details

def phone_number_details():
    phone_number = input("Enter the phone number (with country code, e.g., +14155552671): ")
    country_code = input("Enter the country code (e.g., US, IN, FR): ").upper()
    print(f"Fetching details for phone number: {phone_number} with country code: {country_code}")
    
    details = get_phone_details(phone_number, country_code)
    
    if 'error' in details:
        print(f"Error: {details['error']}")
    else:
        print(f"\nDetails for phone number {phone_number}:")
        print(f"Location: {details['location']}")
        print(f"Carrier: {details['carrier']}")
        print(f"Timezone: {', '.join(details['timezone'])}")

def main():
    print('''
        __  __          _       _                _             
    .___          .__.__                         
  __| _/_______  _|__|  |     ____ ___.__. ____  
 / __ |/ __ \  \/ /  |  |   _/ __ <   |  |/ __ \ 
/ /_/ \  ___/\   /|  |  |__ \  ___/\___  \  ___/ 
\____ |\___  >\_/ |__|____/  \___  > ____|\___  >
     \/    \/                    \/\/         \/ 
                                 
      _                _                      _   _             _    _              _  _   
     | |              | |                    | | | |           | |  | |            | || |  
   __| | _____   _____| | ___  _ __   ___  __| | | |__  _   _  | | _| |__ ______  _| || |_ 
  / _` |/ _ \ \ / / _ \ |/ _ \| '_ \ / _ \/ _` | | '_ \| | | | | |/ / '_ \_  /\ \/ /__   _|
 | (_| |  __/\ V /  __/ | (_) | |_) |  __/ (_| | | |_) | |_| | |   <| |_) / /  >  <   | |  
  \__,_|\___| \_/ \___|_|\___/| .__/ \___|\__,_| |_.__/ \__, | |_|\_\_.__/___|/_/\_\  |_|  
                              | |                        __/ |                             
                              |_|                       |___/       
                                                                
1: Username Finder
2: Account Details Fetcher
3: Phone Number Details Fetcher
          
    ''')
    
    choice = input("What tool do you want to use? : ")
    print(f"User chose option: {choice}")

    try:
        if choice == '1':
            print("Running Username Finder...")
            username_finder()
        elif choice == '2':
            print("Running Account Details Fetcher...")
            account_details_fetcher()
        elif choice == "3":
            print("Running Phone Number Details Fetcher...")
            phone_number_details()
        else:
            print("Invalid choice. Exiting.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
