  for dir in $(ls data); do 
    [[ ! -d "auto/$dir" ]] && mkdir auto/$dir
    ./scripts/meta2bibtex.py data/$dir/final $dir
  done
