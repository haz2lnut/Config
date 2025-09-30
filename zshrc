## Path
CONFIG_PATH=$HOME/.config
PATH="$HOME/.local/bin:$PATH"

## OMZ
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME='simple'
plugins=(git tmux tinted-shell)
ZSH_TMUX_AUTOSTART=true
ZSH_TMUX_FIXTERM_WITH_256COLOR=tmux-256color
source $ZSH/oh-my-zsh.sh

## Alias
alias vi='vim'
alias rm='trash'
alias ls="${aliases[ls]} --group-directories-first"
alias pacman='sudo pacman'
alias svi='sudo vim'
alias systemctl='sudo systemctl'
alias journalctl='sudo journalctl'
alias ll='ls -lah'
alias l='ls -lh'
alias python='python3'
cd() { builtin cd "$@"; l; }

update() {
  pacman --noconfirm -Qdtq | ifne sudo pacman -Rns -
  pacman --noconfirm -Syu
  yay -Sua

  vim -E +PluginUpdate +qall

  ~/.tmux/plugins/tpm/bin/update_plugins all

  python ~/.vim/bundle/YouCompleteMe/install.py --clangd-completer --ts-completer --quiet

  omz update
}

keebuild() {
  [[ $# -eq 1 && ( $1 == 'left' || $1 == 'right' ) ]] || {
    echo "Usage: $0 [left|right]" return 1
  }
  FIRMWARE="$HOME/firmware/nice_view-corne_choc_pro_$1-zmk.uf2"

  DEV=$(lsblk -o NAME,LABEL -nr | awk '$2=="KEEBART" {print $1; exit}')
  if [[ -n $DEV ]]; then
    MNT=/mnt
    sudo mount "/dev/$DEV" /mnt
    sudo cp "$FIRMWARE" /mnt
    sudo umount /mnt
    echo 'done'
  else
    echo 'WTF'
  fi
}

keebedit() {
  vi $HOME/.keeb
}

mkvenv() {
  python -m venv $CONFIG_PATH/venv/$1
  source $CONFIG_PATH/venv/$1/bin/activate
}

venv() {
  source $CONFIG_PATH/venv/$1/bin/activate
}

x() {
  echo $(($1))
}
