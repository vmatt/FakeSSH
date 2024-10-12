def cmd_response():
    return """
Error: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)\r
Error: Unable to lock directory /var/lib/apt/lists/\r
Warning: Problem unlinking the file /var/cache/apt/pkgcache.bin - RemoveCaches (13: Permission denied)\r
Warning: Problem unlinking the file /var/cache/apt/srcpkgcache.bin - RemoveCaches (13: Permission denied)
    """
