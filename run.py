import sys
from load_data import loadData
from nightowl.app import app

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'insert_test_data':
            loadData('instance')
    else:
        app.run()
