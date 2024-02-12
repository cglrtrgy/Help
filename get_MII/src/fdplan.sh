#/usr/bin/env bash

# path to fast downward #
# FD_PATH=$(locate fast-downward.py | head -n 1)

FD_PATH=/s/chopin/b/grad/tcaglar/downward/fast-downward.py

# find optimal plan using fd on input domain and problem #
rm -f output output.sas sas_plan
${FD_PATH} $1 $2 --search "astar(hmax())" | grep -e \([0-9]\) | awk '{$NF=""; print $0}'


# result:
# pickup b 
# stack b a 
# pickup c 
# stack c b 
# pickup d 
# stack d c