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
    echo "[2] Format check for dual mode exercises"
    echo "[3] Format check for \\\\ inside verbatim blocks in all exercises"
    echo "[4] Attempt extraction to CSV"
    echo "==============================================================="
    read -p "Choose operation: " choice

    case $choice in
        0)
            clear
            exit 0
            ;;
        1)
            python3 $checker $src
            read -p "Press Enter to continue..."
            ;;
        2) 
            python3 $checker $src | grep dual
            if [ $? -eq 1 ]; then
                echo "There are no dual mode exercises."
            fi

            read -p "Press Enter to continue..."
            ;;
        3)
            python3 $checker $src | grep verbatim
            if [ $? -eq 1 ]; then
                echo "All verbatim block are clean."
            fi
            read -p "Press Enter to continue..."
            ;;
        4)
            python3 $extractor $src $dest
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Try again."
            sleep 1
            ;;
    esac
done