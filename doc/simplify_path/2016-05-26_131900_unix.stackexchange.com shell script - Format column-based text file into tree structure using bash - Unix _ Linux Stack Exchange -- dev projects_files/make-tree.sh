#!/usr/bin/env bash
# http://unix.stackexchange.com/a/209149

function indent() 
{ 
    ind=$(printf "%*s" "$1" '') 
    printf "${ind// /$'\t'}"
}

while IFS=$'\t' read -a f
do
    # Debug ..
    # printf "[%s] [%s]" "$f" "${#f}"
    for ((i=0; i<${#f}; i++))
    do
        # Debug ..
        # printf "[%s] [%s]\n" "$i" "${f[i]}"
        if [[ "${f[i]}" != "${o[i]}" ]]
        then
            printf "%s%s\n" "$( indent "$i" )" "${f[i]}"
            o[i]=${f[i]}
        fi
    done
done
