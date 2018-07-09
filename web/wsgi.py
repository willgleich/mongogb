#!/usr/bin/env python

'''
Author: William Gleich
Description of wsgi.py :
'''

from app import app

if __name__ == '__main__':
    app.run(host='127.0.0.1')