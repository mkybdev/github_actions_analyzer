del=false

while getopts d flag
do
    case "${flag}" in
        d) del=true;;
    esac
done

find $1 -depth -type d | awk -F / 'NF>=p; {p=NF}' > dirs.dat
if [ -d "../tests/gaa-test-data" ] && [ $del ]; then
  rm -rf ../tests/gaa-test-data
fi

input="dirs.dat"
idx=0
while IFS= read -r line
do
  mkdir -p ../tests/gaa-test-data/${idx}
  cp -pR ${line}/* ../tests/gaa-test-data/${idx}
  idx=$((idx+1))
done < "$input"