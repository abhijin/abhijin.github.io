#!/bin/bash
python2.7 ../packages/jemdoc/jemdoc.py index;
python2.7 ../packages/jemdoc/jemdoc.py pubs;
python2.7 ../packages/jemdoc/jemdoc.py bio;

rsync -av index.html /Volumes/aa5ts/myweb/html/
rsync -av pubs.html /Volumes/aa5ts/myweb/html/
rsync -av bio.html /Volumes/aa5ts/myweb/html/
rsync -av ../cv/cv_abhijin_web.pdf /Volumes/aa5ts/myweb/html/
rsync -av papers/*pdf /Volumes/aa5ts/myweb/html/papers/

## if [[ $1 = "pub" ]]; then
## scp MENU style.css index.html pubs.html bio.html \
##     abhijin.jpg ../cv/cv_abhijin_web.pdf staff.vbi.vt.edu:html/
## scp papers/*pdf staff.vbi.vt.edu:html/papers/
## fi
