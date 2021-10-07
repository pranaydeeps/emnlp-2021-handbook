for file in $(ls data); do 
    echo $file
    cat data/$file/order | ./scripts/verify_schedule.py
done
