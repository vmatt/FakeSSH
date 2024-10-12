def disk_handler():
    return """
Filesystem      Size  Used Avail Use% Mounted on\r
/dev/nvme0n1p1   50G   12G   35G  26% /\r
tmpfs           2.0G     0  2.0G   0% /dev/shm\r
tmpfs           395M  1.1M  394M   1% /run\r
tmpfs           5.0M     0  5.0M   0% /run/lock\r
/dev/nvme1n1p1  100G   40G   58G  41% /data\r
/dev/nvme2n1p1   20G  8.5G   11G  45% /var\r
/dev/nvme0n1p2  500M  120M  380M  24% /boot/efi\r
tmpfs           395M   64K  395M   1% /run/user/1000
    """

def memory_haneler():
    return """
             total        used        free      shared  buff/cache   available\r
Mem:         8038552     4203648     1672720      473108     2929228     3834904\r
Swap:        1000444           0     1000444
    """
