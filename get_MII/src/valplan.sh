# path to fast downward #
VAL_PATH=/Users/turgaycaglar/Documents/VAL-master/build/macos64/Release/Val--Darwin/bin/Validate

# validate plan given domain and problem
output=$(${VAL_PATH} $1 $2 $3 | grep "Successful plans:"|wc -l)

if [ ${output} -gt 0 ]; then
    echo "True"
else
    echo "False"
fi
