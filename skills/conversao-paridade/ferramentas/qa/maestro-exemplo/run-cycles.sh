#!/bin/zsh
# usage: run-cycles.sh <device-id> <DEV label> <appId> <cycles...>
cd "$(dirname $0)"
D=$1; DEV=$2; APP=$3; shift 3
M=~/.maestro/bin/maestro
for c in "$@"; do
  case $c in
    halloween) PLAY="PLAY TRILHA DOS BICHOS"; ARROW=arrow-yellow; TRAP=idle; CAP="CREATURE TRAPPED"; END=hallow;;
    xmas) PLAY="PLAY XMAS TRAIL"; ARROW=arrow-red; TRAP=idle; CAP="CREATURE TRAPPED"; END=xmas;;
    easter) PLAY="PLAY EASTER TRAIL"; ARROW=arrow-red; TRAP=trap-default-easter; CAP="(?s).*Easter Egg.*"; END=easter;;
    july4) PLAY="${PLAY_J4:-PLAY JULY4 TRAIL}"; ARROW=arrow-red; TRAP=trap-default-july4; CAP="Pin Collected"; END=july4;;
  esac
  if [[ $APP == com.exemplo.trilhadosbichos ]]; then CPOINT="79%,42%"; FILES=(part1-start.yaml part2-play-android.yaml part3-end-android.yaml part4-finish-android.yaml)
  else CPOINT="85%,50%"; FILES=(part1-start.yaml part2-play.yaml part3-end-$END.yaml part4-finish.yaml); fi
  for f in $FILES; do
    echo "=== $DEV $c $f"
    $M --device $D test -e APP=$APP -e DEV=$DEV -e THEME=$c -e "PLAY=$PLAY" -e ARROW=$ARROW -e TRAP=$TRAP -e "CAPTEXT=$CAP" -e "CPOINT=$CPOINT" $f > logs/$DEV-$c-$f.log 2>&1
    if grep -q FAILED logs/$DEV-$c-$f.log; then echo "FAILED $DEV $c $f"; cp "$(ls -td ~/.maestro/tests/*/ | head -1)"/*.png shots/$DEV/$c-FAIL-$f.png 2>/dev/null; break; fi
  done
done
echo DONE $DEV
