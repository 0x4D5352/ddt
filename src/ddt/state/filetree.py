"""
Three data stuctures:
All Files - a set of files (Path)
Excluded files - a list/set of files (Path)
Included files - a list/set of files (Path)

Logic:
take a FileTree.All Files and separate it out to Excluded Files and Included Files

Input:

- Set of files

Logic:

1. filter excluded files to get initial included/excluded list
2. if custom inclusions exist, filter included files to get added exclusions and new included list.
3. Pass excluded to Result.NotCounted
"""
