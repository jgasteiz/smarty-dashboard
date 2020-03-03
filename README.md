# SMARTY home dashboard

This is a simple Flask application for getting the remaining data usage on a user's account.

At the moment it simply returns the usage as a string, but ideally this will be used together with Google Home and/or Amazon Alexa.

## How to use

- Rename the `.env.example` file to `.env`.
- Fill in credentials.
- Create virtualenv and install dependencies:
  - `mkvirtualenv smarty`
  - `pip install -r requirements.txt`
- Serve: `make serve`
