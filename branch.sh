#!/bin/sh
set -e
svn=http://varnish.projects.linpro.no/svn
tag=varnish-2.0.6/varnish-cache
branch=2.0/varnish-cache
out=branch.diff

d=$-
filter() {
	set -$d
	# Excluding files which change version or were not in dist tarball
	filterdiff \
		-x 'nothing' \
		| \
	# remove revno's for smaller diffs
	sed -e 's,^\([-+]\{3\} .*\)\t(revision [0-9]\+)$,\1,'
}

old=$svn/tags/$tag
new=$svn/branches/$branch
echo >&2 "Running diff: $old -> $new"
LC_ALL=C svn diff --old=$old --new=$new > $out.tmp
revno=$(sed -ne 's,^[-+]\{3\} .*\t(revision \([^0][0-9]*\))$,\1,p' $out.tmp | sort -u)
echo >&2 "Revision $revno"
sed -i -e "1i# Revision $revno" $out.tmp
filter < $out.tmp > $out.tmp2 && mv -f $out.{tmp2,tmp}

if cmp -s $out{,.tmp}; then
	echo >&2 "No new diffs..."
	rm -f $out.tmp
	exit 0
fi
mv -f $out{.tmp,}
