#!/usr/bin/env python

from fastcore.script import *

@call_parse
def main(
    msg:str, # The message
    upper:bool # Convert to uppercase?
):
    "Print `msg`, optionally converting to uppercase"
    print(msg.upper() if upper else msg)

