#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <passphrase_or_key> <directory>"
    exit 1
fi

passphrase="$1"
directory="$2"

find "$directory" -type f -name "*.planted" | while read -r encrypted_file; do
    filename=$(basename "$encrypted_file" .planted)

    gpg --batch --passphrase "$passphrase" --output "${encrypted_file%.planted}" --decrypt "$encrypted_file"

    if [ $? -eq 0 ]; then
        echo "File '$filename' decrypted and restored successfully."
    else
        echo "Decryption failed for file '$filename'. Check the passphrase or key."
    fi
done

