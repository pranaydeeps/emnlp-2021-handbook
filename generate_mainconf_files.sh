 for name in papers; do
     cat data/$name/order | ./scripts/order2schedule_overview.py
 done
