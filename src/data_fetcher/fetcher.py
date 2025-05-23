import asyncio
import os
from dotenv import load_dotenv
from twscrape import API, AccountsPool 


load_dotenv()


async def get_api_client() -> API | None:
    """
    Helper function to initialize and return a twscrape API client.
    IMPORTANT: You must add your X account(s) here for twscrape to work.
    """
    print("Initializing twscrape API client...")
    current_pool = AccountsPool() 

    try:
        x_username = os.getenv("X_USERNAME")
        x_password = os.getenv("X_PASSWORD")
        x_email = os.getenv("X_EMAIL")
        x_email_password = os.getenv("X_EMAIL_PASSWORD")
        
        if not all([x_username, x_password, x_email, x_email_password]):
            raise ValueError("Missing X account credentials in environment variables. Please set X_USERNAME, X_PASSWORD, X_EMAIL, and X_EMAIL_PASSWORD in your .env file.")
        
        await current_pool.add_account(x_username, x_password, x_email, x_email_password)

        
        await current_pool.login_all() 

        api_client = API(current_pool)
        print("API client initialized successfully.")
        return api_client

    except Exception as e:
        print(f"Error during API client initialization (add or login): {type(e).__name__} - {e}")
        return None

async def fetch_user_details(username: str) -> dict[str, str | None] | None:
    """
    Fetches the bio, profile image URL, and display name of a given X user.
    Returns a dictionary with these details or None if the user is not found or an error occurs.
    """
    print(f"Fetching details for {username} using twscrape...")
    api = await get_api_client()

    try:
        user = await api.user_by_login(username)
        if user:
            details = {
                "bio": user.rawDescription if hasattr(user, 'rawDescription') else None,
                "profile_image_url": user.profileImageUrl if hasattr(user, 'profileImageUrl') else None,
                "display_name": user.displayname if hasattr(user, 'displayname') else None
            }

            return details
        else:
            print(f"User {username} not found (api.user_by_login returned None).")
            return None
    except Exception as e:
        print(f"Error fetching details for {username}: {type(e).__name__} - {e}")
        return None

async def fetch_recent_tweets(username: str, n: int = 10) -> list[str]:
    """
    Fetches the N most recent tweets for a given X user.
    Returns a list of tweet text strings.
    """
    print(f"Fetching {n} tweets for {username} using twscrape...")
    api = await get_api_client()
    if not api:
        print("Failed to initialize twscrape API client.")
        return []
    
    tweets_content = []
    try:
        # First, get the user object to retrieve their ID, as user_tweets usually takes user_id
        user = await api.user_by_login(username)
        if not user or not hasattr(user, 'id'):
            print(f"User {username} not found or ID missing, cannot fetch tweets.")
            return []

        user_id = user.id
        i = 0
        async for tweet in api.user_tweets(user_id, limit=n):
            if hasattr(tweet, 'rawContent') and tweet.rawContent:
                tweets_content.append(tweet.rawContent)
                i += 1
                if i == n:
                    break

        if not tweets_content:
            print(f"No tweets found for {username} (or tweets had no text content).")
 
        return tweets_content

    except Exception as e: # Generic exception handler
        print(f"Error fetching tweets for {username}: {type(e).__name__} - {e}")
        return []

