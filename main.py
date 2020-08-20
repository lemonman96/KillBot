from killbot import Bot
import sys

def main(argv):
    bot = Bot()
    bot.run()

if __name__ == "__main__":
   main(sys.argv[1:])