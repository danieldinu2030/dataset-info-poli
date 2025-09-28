#!/bin/bash

src_1="enunturi.tex"
src_2="solutii.tex"
checker="checker_enunturi.py"
extr_1="extract_enunturi.py"
extr_2="extract_solutii.py"
dest_1="enunturi.csv"
dest_2="solutii.csv"

while true; do
    clear
    echo "==============================================================="
    echo "Possible operations:"
    echo "[0] Exit"
    echo "[1] Full format check for all exercises"
    echo "[2] Full format check for one set of exercises"
    echo "[3] Format check for dual mode exercises"
    echo "[4] Format check for trio mode exercises"
    echo "[5] Find out which exercises are missing"
    echo "[6] Find out which solutions are missing"
    echo "[7] Attempt exercise extraction to CSV"
    echo "[8] Attempt solution extraction to CSV"
    echo "==============================================================="
    read -p "Choose operation: " choice

    case $choice in
        0)
            clear
            exit 0
            ;;
        1)
            python3 $checker $src_1 | grep not
            if [ $? -eq 1 ]; then
                echo "All exercises match."
            fi
            read -p "Press Enter to continue..."
            ;;
        2)
            read -p "Choose exercise set number: " set
            python3 $checker $src_1 | grep "^$set\."
            if [ $? -ne 0 ]; then
                echo "The exercise set with this number doesn't exist or there was an error."
            fi
            read -p "Press Enter to continue..."
            ;;
        3) 
            python3 $checker $src_1 | grep dual | grep not
            if [ $? -eq 1 ]; then
                echo "All dual mode exercises match."
            fi
            read -p "Press Enter to continue..."
            ;;
        4)
            python3 $checker $src_1 | grep trio | grep not
            if [ $? -eq 1 ]; then
                echo "All trio mode exercises match."
            fi
            read -p "Press Enter to continue..."
            ;;
        5)
            read -p "Enter number of exercise sets (at least 1): " sets
            read -p "Enter number of exercises in a set (at least 1): " number
            for x in $(seq 1 $sets); do
                for y in $(seq 1 $number); do
                    pattern="^$x\.$y\."
                    if ! grep -qE "$pattern" $src_1; then
                        echo "Could not find exercise $x.$y."
                    fi
                done
            done
            read -p "Press Enter to continue..."
            ;;
        6)
            read -p "Enter number of exercise sets (at least 1): " sets
            read -p "Enter number of exercises in a set (at least 1): " number
            for x in $(seq 1 $sets); do
                for y in $(seq 1 $number); do
                    pattern="^$x\.$y\."
                    if ! grep -qE "$pattern" $src_2; then
                        echo "Could not find solution $x.$y."
                    fi
                done
            done
            read -p "Press Enter to continue..."
            ;;
        7)
            python3 $extr_1 $src_1 $dest_1
            read -p "Press Enter to continue..."
            ;;
        8)
            python3 $extr_2 $src_2 $dest_2
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Try again."
            sleep 1
            ;;
    esac
done