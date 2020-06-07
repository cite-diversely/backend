QUERY='bib=@inproceedings{Parhi2006,
author = {Parhi, Pekka and Karlson, Amy K. and Bederson, Benjamin B.},
booktitle = {Proceedings of the 8th Conference on Human-Computer Interaction with Mobile Devices and Services - MobileHCI},
doi = {10.1145/1152215.1152260},
pages = {203-210},
title = {Target size study for one-handed thumb use on small touchscreen devices},
volume = {159},
year = {2006}
}'

curl http://localhost:5000/ --data-urlencode "$(echo $QUERY)" -X POST -v