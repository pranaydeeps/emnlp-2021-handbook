for dir in $(ls data); do 
   [[ ! -d "auto/$dir" ]] && mkdir auto/$dir
   cat data/$dir/\order | ./scripts/order2schedule_workshop.pl $dir > auto/$dir/schedule.tex
done
