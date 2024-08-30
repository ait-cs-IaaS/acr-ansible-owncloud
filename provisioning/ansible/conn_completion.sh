# conn-completion.sh

_conn_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=$(awk '!/^\s*$|Name/ {print $1}' ~/infra)

    if [ "$prev" == "-j" ]; then
        # List jumphost options
        COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
        return 0
    elif [ "$prev" == "conn" ]; then
        # List target host options
        COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
        return 0
    fi
}
complete -F _conn_complete conn
