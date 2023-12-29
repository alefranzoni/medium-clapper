[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Donate][donate-shield]][donate-url]

# Medium Clapper
Are you a big fan of a content creator on Medium? Then **Medium Clapper** can be your best friend. This is a tool developed to make the clapping process easier for you. All you have to do is run the script, give them a few commands and let it do the rest for you!

## Contents
- [Medium Clapper](#medium-clapper)
  - [Contents](#contents)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Examples](#examples)
  - [First time: What do I need to know?](#first-time-what-do-i-need-to-know)
    - [How do we generate a new security key?](#how-do-we-generate-a-new-security-key)
    - [Considerations](#considerations)
  - [Roadmap](#roadmap)
  - [Disclaimer](#disclaimer)
  - [Donate](#donate)

## Requirements
This tool uses Python, Playwright and a few more libraries to do its job. Below the list of dependencies you need to have installed in order to use it. Of course, in addition to these libs, you need `Python3` and `PIP` installed.

```bash
# playwright
pip install playwright
playwright install
# cryptography
pip install cryptography
# requests
pip install requests
```

## Installation
Download this project manually or clone the repo with git

```bash
git clone https://github.com/alefranzoni/medium-clapper.git
```

## Usage
After installing the dependencies, go to the project directory and run the `medium_clapper.py` with Python3

```bash
cd medium-clapper
python3 medium_clapper.py [-h] -t USER_ID [-sd SCROLL_DELAY] [-sr SCROLL_RETRIES] [-c CLAPS] [-rt READ_TIME] [-gk]
```

| Command     | Type  | Mandatory | Description                                                             |
|-------------|-------|-----------|-------------------------------------------------------------------------|
|`-t`         |String | **Yes**   |Target username (including `@` if needed)                                |
|`-sd`        |Float  | -         |Adds a delay (in seconds) to the scrolling process. Default: 0.85        |
|`-sr`        |Int    | -         |Adds attempts to the scrolling process. Default: 3                       |
|`-c`         |Int    | -         |Number of claps to give. Default: 50                                     |
|`rt`         |Float  | -         |Time in seconds to wait in article to emulate reading time. Default is 10|
|`-gk`        |Boolean| -         |Generate a new passkey to protect PII data                               |

> Notice that the delay or retries options are similar and **do not** replace the default values, but are added to them. In slow connections, we can increase one or both of these values. Remember that setting very high values for either of these two options will cause the required processing times to be longer.

### Examples
```bash
# without passing any args but the mandatory
python3 medium_clapper.py -t @alefranzoni
# changing claps and read time
python3 medium_clapper.py -t @alefranzoni -c 10 -rt 3
```

## First time: What do I need to know?
As the tool stores cookies locally to save session data, thus avoiding having to log in to your account at each run, it is imperative that this data is protected from prying eyes. To achieve this, the data is encrypted with a unique, personal key. We only need to generate it for the **first and only time** and then save it, either in the default directory or in a secure location.

### How do we generate a new security key?
To generate a new security key, it is as simple as running the script with the desired options and including the `-gk` argument. This will automatically generate your personal key and store it in the `./data` folder.

```bash
# example - generate new passkey
python3 medium_clapper.py -t @alefranzoni -gk
```

### Considerations
- If we move the security key to another place, before each execution we must place it in the `./data` folder.
- If we lose the key, we can always generate a new one, but the session data previously protected with the old key will be lost.

## Roadmap
What's the upcoming features that I have in mind?
- [ ] Get the reading time (calculated by Medium) of each article.
- [ ] Improve the clapping process by obtaining the number of claps given, this way if you have already given the maximum number of claps, do not waste time and continue with the next one.

## Disclaimer
The use of this tool should not present any problems, however, it should be used at the **user's discretion**. The author assumes no liability for any claims, damages, or any other inconveniences that may occur.

## Donate
You can support me through [**Cafecito**](https://cafecito.app/alefranzoni) (🇦🇷) or [**PayPal**](https://www.paypal.com/donate/?hosted_button_id=9LR86UDHEKM3Q) (Worldwide). Thank you ❤️

[stars-shield]: https://img.shields.io/github/stars/alefranzoni/medium-clapper
[stars-url]: https://github.com/alefranzoni/medium-clapper/stargazers
[issues-shield]: https://img.shields.io/github/issues/alefranzoni/medium-clapper
[issues-url]: https://github.com/alefranzoni/medium-clapper/issues
[donate-shield]: https://img.shields.io/badge/$-donate-ff69b4.svg?maxAge=2592000&amp;style=flat
[donate-url]: https://github.com/alefranzoni/medium-clapper#donate
