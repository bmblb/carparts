import sys, os

sys.path.append(os.path.join(os.getcwd(), 'app'))

from app.main import main

if not os.path.exists('log'):
    os.makedirs('log')
    with open('log/parser.log', 'w', newline='', encoding='utf-8') as logfile:
        logfile.write('')

if __name__ == '__main__':
    main()
