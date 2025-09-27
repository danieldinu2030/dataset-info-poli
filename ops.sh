#!/bin/bash

src="enunturi.tex"
checker="checker_enunturi.py"
extractor="extract_enunturi.py"
dest="enunturi.csv"

while true; do
    clear
    echo "==============================================================="
    echo "Possible operations:"
    echo "[0] Exit"
    echo "[1] Full format check for all exercises"
    echo "[2] Full format check for one set of exercises"
    echo "[3] Format check for dual mode exercises"
    echo "[4] Format check for trio mode exercises"
    echo "[5] Attempt extraction to CSV"
    echo "[6] Find out which exercises are missing"
    echo "==============================================================="
    read -p "Choose operation: " choice

    case $choice in
        0)
            clear
            exit 0
            ;;
        1)
            python3 $checker $src | grep not
            if [ $? -eq 1 ]; then
                echo "All exercises match."
            fi
            read -p "Press Enter to continue..."
            ;;
        2)
            read -p "Choose exercise set number: " set
            python3 $checker $src | grep "^$set\."
            if [ $? -ne 0 ]; then
                echo "The exercise set with this number doesn't exist or there was an error."
            fi
            read -p "Press Enter to continue..."
            ;;
        3) 
            python3 $checker $src | grep dual | grep not
            if [ $? -eq 1 ]; then
                echo "All dual mode exercises match."
            fi
            read -p "Press Enter to continue..."
            ;;
        4)
            python3 $checker $src | grep trio | grep not
            if [ $? -eq 1 ]; then
                echo "All trio mode exercises match."
            fi
            read -p "Press Enter to continue..."
            ;;
        5)
            python3 $extractor $src $dest
            read -p "Press Enter to continue..."
            ;;
        6)
            read -p "Enter number of exercise sets (at least 1): " sets
            read -p "Enter number of exercises in a set (at least 1): " number
            for x in $(seq 1 $sets); do
                for y in $(seq 1 $number); do
                    pattern="^$x\.$y\."
                    if ! grep -qE "$pattern" $src; then
                        echo "Could not find exercise $x.$y."
                    fi
                done
            done
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Try again."
            sleep 1
            ;;
    esac
done