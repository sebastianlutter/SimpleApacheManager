#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convenience wrapper for running Simple Apache Manager directly from source tree."""

# change execution directory to the parent folder of this file
import os
parent_dir=os.path.dirname(os.path.realpath(__file__))
os.chdir(parent_dir)

from sam.SimpleApacheManager import main
# start SimpleApacheManager
if __name__ == '__main__':
    main()