#!/bin/bash
# md5.sh <relpath trong wp-content>...  -> md5 8 ký tự của file production (DIR cho thư mục, ABSENT nếu không có)
P=${DOCROOT:?DOCROOT}/wp-content
for r in "$@"; do if [ -f "$P/$r" ]; then echo "$(md5sum "$P/$r" | cut -c1-8) $r"; elif [ -d "$P/$r" ]; then echo "DIR $r"; else echo "ABSENT $r"; fi; done
