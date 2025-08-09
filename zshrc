## Path
CONFIG_PATH=$HOME/.config
PATH="$HOME/.local/bin:$PATH"
eval "$(/opt/homebrew/bin/brew shellenv)"

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
alias ls="${aliases[ls]}"
alias ll='ls -lah'
alias l='ls -lh'
alias python='python3'
cd() { builtin cd "$@"; ls; }


update() {
  brew update
  brew upgrade

  vim -E +PluginUpdate +qall

  python ~/.vim/bundle/YouCompleteMe/install.py --clangd-completer --quiet

  omz update

  command rm -f ~/.zcompdump
  compinit
}

keebuild() {
  QMK_PATH=$HOME/.qmk
  KEYMAP_PATH=$QMK_PATH/keyboards/keyboardio/atreus/keymaps/haz2lnut

  pushd $QMK_PATH
  git pull
  command cp -a $CONFIG_PATH/keymap $KEYMAP_PATH
  docker run --rm -it -w /qmk_firmware -v $QMK_PATH:/qmk_firmware:z ghcr.io/qmk/qmk_cli make keyboardio/atreus:haz2lnut
  command rm -rf $KEYMAP_PATH
  command mv $QMK_PATH/*.hex ~/Downloads/
  popd
}

keebedit() {
  vi $CONFIG_PATH/keymap
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

vault() {
  case $1 in
    edit)
      vi $HOME/.vault
      return
      ;;
  esac

  pushd $HOME/Blog
  venv Blog
  flask "$@"
  deactivate
  popd
}
# The following lines have been added by Docker Desktop to enable Docker CLI completions.
fpath=(/Users/haz2lnut/.docker/completions $fpath)
autoload -Uz compinit
compinit
# End of Docker CLI completions
