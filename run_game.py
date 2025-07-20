import os
import sys

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import start_screen
        start_screen.main()
    except ImportError:
        print("Can't find start_screen.py")
        sys.exit(1)
    except Exception as e:
        print(f"Something went wrong: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
