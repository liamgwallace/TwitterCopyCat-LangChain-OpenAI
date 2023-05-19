# Tweet Generation Program

This is a Python program that generates tweets in the style of a given Twitter user. It utilizes OpenAI's language model (GPT-3.5) to mimic the author's tone and generate new tweets.

## Features

- Retrieve original tweets from a Twitter user
- Analyze the author's tone based on the tweets
- Generate new tweets in the same style as the examples
- Generate subjects for new tweets based on the examples

## Requirements

- Python 3.x
- OpenAI Python library (installation instructions [here](https://github.com/openai/openai-python))
- Tweepy Python library (installation instructions [here](https://github.com/tweepy/tweepy))

## Setup

1. Clone the repository
git clone https://github.com/your-username/tweet-generation-program.git

2. Install the required Python and the libraries
pip install -r requirements.txt

3. Set up your API keys and access tokens
- OpenAI API Key: Obtain an API key from the OpenAI website.
- Twitter API Credentials: Create a Twitter Developer account and obtain the necessary credentials

4. Update the following variables in the `.env` file
- rename 'template.env' file to just '.env'
- `openai_api_key` - Set this variable to your OpenAI API key.
- `TWITTER_BEARER_TOKEN` - Set this variable to your Twitter Bearer Token.

## Usage

Run the program by executing the `main.py` file
python main.py

- Enter a Twitter screen name when prompted.
- The program will retrieve the original tweets from the user and analyze the author's tone.
- It will generate new tweets in the same style as the examples and display them.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please create an issue or submit a pull request.

## License

Whatever, just dont blame me
