# BetFiery CrashGame auto bet

## Aplicativo para gestão programada de banca

## To run

Download [chrome webdriver](https://chromedriver.chromium.org/downloads), and save on src/utils path with name chromedriver.exe

We recomendly use python venv during install the bot dependencies

    python -m venv venv
    venv\Scripts\activate (CMD)
    source venv/bib/activate (BASH)

On folder src:

1. Create .env file with environment variables. See configs file to view a resume of vars. 
2. Config saque vars on .env, with your data based on form saque of betfiery platform

    python bot.py