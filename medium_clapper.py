import sys
from modules.argument_manager import ArgumentManager, ArgumentOptions
from modules.session_utils import check_security_key_exists, generate_security_key
from modules.scraper import Scraper

def main():
    """
    Entry point of the program.
    Manages arguments, handles security key, and starts the scraper.
    """
    args = ArgumentManager()
    handle_security_key(generate_key_arg=args.get(ArgumentOptions.GENERATE_KEY))
    scraper = Scraper(arguments=args)
    scraper.start()

def handle_security_key(generate_key_arg):
    """
    Handles the existence and generation of a security key based on 
    the provided argument.
    """
    key_exists=check_security_key_exists()
    if not key_exists and not generate_key_arg:
        print("🚨 The security key has not been found. Generate or place it inside the data folder."
            "\n → More information at https://github.com/alefranzoni/medium-clapper")
        sys.exit()
    elif generate_key_arg:
        if key_exists:
            generate_new_key = ""
            while generate_new_key not in ["y", "n"]:
                generate_new_key = input(
                    "🚨 You have already generated a security key! "
                    "Do you want to generate a new one and replace it? (y/n): "
                ).lower().strip()
            if generate_new_key == "y":
                generate_security_key()
        else:
            generate_security_key()

if __name__ == "__main__":
    main()
