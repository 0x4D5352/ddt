"""
Two categories of Input:
    - Multiple Files:
        a. single directory
        b. list of directories
        c. list of files
    - Single File:
        a. single file
        b. std input


Logic:

0. Does root not exist but stdin does? If so, treat stdin as root.
1. Take `root` and try to convert it to a path.
2. Is it a resolvable path?
    2a. If yes, is it a directory?
        - If yes, glob and pass a set of all files to FileTree.All Files
        - If no, pass to TokenCounter.Parser
    2b. If no, is it json, csv, or text?
        - if JSON or CSV, repeat step 2 for each item
        - if text, split on space and repeat step 2 for each item
        - for both, count length before iterating and reject if over some arbitrary limit
        - for both, track Not A File count. 
            - If exceeded, pass original results to TokenCounter.Parser
3. Take final list from 2b and pass a set of all files to FileTree.All Files
"""
