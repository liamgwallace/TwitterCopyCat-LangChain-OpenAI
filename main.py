# Import necessary libraries

import argparse  # Library for parsing command-line arguments
from dotenv import load_dotenv  # Library for loading environment variables from a .env file
import os  # Library for interacting with the operating system
import tweepy  # Library for accessing the Twitter API
from langchain.chat_models import ChatOpenAI  # Custom library for chat models
from langchain import LLMChain  # Custom library for language models
from langchain import PromptTemplate  # Custom library for prompt templates
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)  # Custom library for chat prompt templates
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)  # Custom library for chat schema
import requests  # Library for making HTTP requests
import json  # Library for working with JSON data

# Load .env file
load_dotenv()

# Set your OpenAI key
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize the LLM
llm_exact = ChatOpenAI(temperature=0, openai_api_key=openai_api_key, model_name='gpt-3.5-turbo')
llm_creative = ChatOpenAI(temperature=1, openai_api_key=openai_api_key, model_name='gpt-3.5-turbo')

# Set your Twitter API credentials
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

def print_verbose(*args):
    """
    Function for printing verbose output.

    Args:
        *args: Variable number of arguments to be printed.
    """
    if verbose:
        print("##############################################################")
        for arg in args:
            if isinstance(arg, list):
                for item in arg:
                    print(item)
            else:
                print(arg)
        print("##############################################################")
    if slow:
        a = input("press enter to continue")

def get_original_tweets(screen_name, tweets_to_pull=70, tweets_to_return=30):
    """
    Function to retrieve original tweets from a Twitter user.

    Args:
        screen_name (str): Twitter screen name of the user.
        tweets_to_pull (int): Number of tweets to pull from the user's timeline (default: 70).
        tweets_to_return (int): Number of tweets to return as examples (default: 30).

    Returns:
        str: Concatenated original tweets from the user.
    """
    # Construct the URL to retrieve user information based on the screen name
    base_url = f"https://api.twitter.com/2/users/by/username/{screen_name}"
    # Send a GET request to retrieve user information
    user_response = requests.get(base_url, headers={"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"})

    # Check if the user information was retrieved successfully
    if user_response.status_code != 200:
        raise Exception(f"Failed to retrieve user information: {user_response.status_code}")
    
    # Extract the user ID from the response
    user_id = user_response.json()["data"]["id"]

    # Construct the URL to retrieve the user's tweets
    tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    # Set the parameters for the tweet retrieval API request
    params = {
        "tweet.fields": "created_at",
        "max_results": tweets_to_pull,
        "expansions": "referenced_tweets.id",
        "media.fields": "url",
        "exclude": "replies,retweets",
    }
    
    # Send a GET request to retrieve the user's tweets
    tweets_response = requests.get(tweets_url, headers={"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}, params=params)

    # Check if the tweets were retrieved successfully
    if tweets_response.status_code != 200:
        raise Exception(f"Failed to retrieve tweets: {tweets_response.status_code}")

    # Extract the tweets data from the response
    tweets_data = tweets_response.json()["data"]
    # Initialize an empty string to store the concatenated tweets
    example_tweets = ""

    # Iterate over the tweets data and concatenate the tweet text
    for tweet in tweets_data:
        # Check if the desired number of tweets to return has been reached
        if len(example_tweets.split("\n")) >= tweets_to_return:
            break

        example_tweets += f"{tweet['text']}\n"
    
    # Return the concatenated tweets, stripped of leading/trailing whitespace
    return example_tweets.strip()
    
def get_authors_tone_description(how_to_describe_tone, users_tweets):
    """
    Function to get the description of the author's tone based on user's tweets.

    Args:
        how_to_describe_tone (str): Instructions on how to describe the tone.
        users_tweets (str): Concatenated original tweets from the user.

    Returns:
        str: Description of the author's tone.
    """
    # Define a template string for the tone description prompt
    template = """
        You are an AI Bot that is very good at generating writing in a similar tone as examples.
        Be opinionated and have an active voice.
        Take a strong stance with your response.

        % HOW TO DESCRIBE TONE
        {how_to_describe_tone}

        % START OF EXAMPLES
        {tweet_examples}
        % END OF EXAMPLES

        List out the tone qualities of the examples above
        """

    # Create a HumanMessagePromptTemplate from the template
    human_message_prompt = HumanMessagePromptTemplate.from_template(template)

    # Create a ChatPromptTemplate from the HumanMessagePromptTemplate
    chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

    # Format the ChatPromptTemplate with the provided instructions and user's tweets
    formatted_prompt = chat_prompt.format_prompt(how_to_describe_tone=how_to_describe_tone, tweet_examples=users_tweets).to_messages()

    # Generate the author's tone description using the LLM
    authors_tone_description = llm_exact(formatted_prompt).content

    print_verbose("authors_tone_description: ", authors_tone_description)

    return authors_tone_description



def generate_tweet_in_style(authors_tone_description, tweet_examples, subject):
    """
    Function to generate a tweet in the style described by the author's tone.

    Args:
        authors_tone_description (str): Description of the author's tone.
        tweet_examples (str): Concatenated original tweets from the user.
        subject (str): The subject of the new tweet.

    Returns:
        str: The generated tweet in the same style as the examples.
    """
    template = """
    % INSTRUCTIONS
     - You are an AI Bot that is very good at mimicking an author writing style.
     - Your goal is to write content with the tone that is described below.
     - These output must be in the style of the examples you are given, but be completely unique 
     - Do not go outside the tone instructions below
    % HOW TO DESCRIBE TONE
    {how_to_describe_tone}

    % START OF EXAMPLES
    {tweet_examples}
    % END OF EXAMPLES

    Write a tweet (under 300 characters) in the same tone as the examples above about {subject} .
    """

    # Create a HumanMessagePromptTemplate from the template
    human_message_prompt = HumanMessagePromptTemplate.from_template(template)

    # Create a ChatPromptTemplate from the HumanMessagePromptTemplate
    chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

    # Format the ChatPromptTemplate with the query
    formatted_prompt = chat_prompt.format_prompt(how_to_describe_tone=authors_tone_description, tweet_examples=tweet_examples, subject=subject).to_messages()

    # Generate a new tweet using the LLM
    new_tweet = llm_creative(formatted_prompt).content

    print_verbose("new_tweet: ", new_tweet)

    return new_tweet

def generate_tweet_subject(tweet_examples, old_subjects):
    """
    Function to generate a subject for a new tweet based on given examples.

    Args:
        tweet_examples (str): Concatenated original tweets from the user.

    Returns:
        str: The unique new subject of a tweet in under 5 words.
    """
    template = """
    % INSTRUCTIONS
     - You are an AI Bot that is very good at coming up with great ideas based on some input examples
     - These ideas must be in the style the examples you are given, but be completely unique 
     - The examples are a guide to show the typical subjects
     - Do not include any words from the examples in your response
     - Your goal is to write a subject for a new tweet based on the examples given
    % START OF EXAMPLES
    {tweet_examples}
    % END OF EXAMPLES

    Write the unique new subject of a tweet in under 4 words.
    It must be COMPLETELY different from these previous subjects: {old_subjects}
    Get creative think about all the subjects used and imagine what else they might talk about
    """

    # Create a HumanMessagePromptTemplate from the template
    human_message_prompt = HumanMessagePromptTemplate.from_template(template)

    # Create a ChatPromptTemplate from the HumanMessagePromptTemplate
    chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

    # Format the ChatPromptTemplate with the query
    formatted_prompt = chat_prompt.format_prompt(tweet_examples=tweet_examples, old_subjects=old_subjects).to_messages()
    # Generate a new subject for the tweets using the LLM
    new_subject = llm_creative(formatted_prompt).content

    print_verbose("new_subject: ", new_subject)

    return new_subject


def main(): 
    """
    Main function to run the tweet generation program.
    """
    # Instructions on how to describe the tone
    how_to_describe_tone = """
        1. Pace: The speed at which the story unfolds and events occur.
        2. Mood: The overall emotional atmosphere or feeling of the piece.
        3. Tone: The author's attitude towards the subject matter or characters.
        4. Voice: The unique style and personality of the author as it comes through in the writing.
        5. Diction: The choice of words and phrases used by the author.
        6. Syntax: The arrangement of words and phrases to create well-formed sentences.
        7. Imagery: The use of vivid and descriptive language to create mental images for the reader.
        8. Theme: The central idea or message of the piece.
        9. Point of View: The perspective from which the story is told (first person, third person, etc.).
        10. Structure: The organization and arrangement of the piece, including its chapters, sections, or stanzas.
        11. Dialogue: The conversations between characters in the piece.
        12. Characterization: The way the author presents and develops characters in the story.
        13. Setting: The time and place in which the story takes place.
        14. Foreshadowing: The use of hints or clues to suggest future events in the story.
        15. Irony: The use of words or situations to convey a meaning that is opposite of its literal meaning.
        16. Symbolism: The use of objects, characters, or events to represent abstract ideas or concepts.
        17. Allusion: A reference to another work of literature, person, or event within the piece.
        18. Conflict: The struggle between opposing forces or characters in the story.
        19. Suspense: The tension or excitement created by uncertainty about what will happen next in the story.
        20. Climax: The turning point or most intense moment in the story.
        21. Resolution: The conclusion of the story, where conflicts are resolved and loose ends are tied up.
    """
    
    while True:
        # Prompt the user to enter a Twitter screen name
        user_screen_name = input(f"\nEnter Twitter screen name: ")
        
        # Retrieve the original tweets from the user
        users_tweets = get_original_tweets(user_screen_name)
        print_verbose("users_tweets: ", users_tweets)
        
        # Get the description of the author's tone based on user's tweets
        authors_tone_description = get_authors_tone_description(how_to_describe_tone, users_tweets)
        print(f"\nNew tweets in the style of @{user_screen_name}")
        # clear the subject list
        subjects = []  # Initialize an empty list

        for i in range(3):
            # Generate the subject for the new tweet
            subject = generate_tweet_subject(users_tweets, subjects)
            
            # Generate the new tweet in the style of the examples
            new_tweet = generate_tweet_in_style(authors_tone_description, users_tweets, subject)
            
            #keep a list of used subjects
            subjects.append(subject)
            print(f"\nSubject: {subject}")
            print(f"{new_tweet}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Search PDF documents with a query.")
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('--slow', dest='slow', action='store_true', help='Enable slow verbose mode')
    parser.set_defaults(verbose=False, slow=False)
    args = parser.parse_args()
    verbose = args.verbose
    slow = args.slow

    # Run the main program
    main()