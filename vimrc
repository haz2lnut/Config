"
" Vundle
"
set nocompatible              " be iMproved, required
filetype off                  " required
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'
Plugin 'tinted-theming/tinted-vim'
Plugin 'preservim/nerdtree'
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'
Plugin 'tpope/vim-surround'
Plugin 'ycm-core/YouCompleteMe'
Plugin 'sheerun/vim-polyglot'
call vundle#end()            " required
filetype plugin indent on    " required


"
" Defaults
"
syntax on
set hlsearch
set incsearch
let mapleader=','
set wildignore=.git,.next,node_modules,__pycache__,.build,.cache,compile_commands.json,*.db,*.o,.eslintrc.json,instance,.DS_Store
autocmd FileType * setlocal ts=2 sts=2 sw=2 expandtab smartindent cindent
autocmd FileType markdown setlocal spell spelllang=en,cjk
autocmd FileType c setlocal noexpandtab cc=80
autocmd FileType cpp setlocal noexpandtab cc=80
autocmd FileType make setlocal noexpandtab cc=80
autocmd BufRead,BufNewFIle *.S setlocal filetype=asm
autocmd BufRead,BufNewFIle *.s setlocal filetype=asm
set autowriteall
autocmd BufLeave,BufWinLeave,InsertLeave,CmdlineEnter * if &filetype != 'nerdtree' && &modifiable && filereadable(bufname('%')) | silent! w | endif
set backspace=indent,eol,start



"
" Nerdtree
"
let g:NERDTreeQuitOnOpen=1
let g:NERDTreeMinimalUI=1
let g:NERDTreeRespectWildIgnore=1
let g:NERDTreeShowHidden=1
let g:NERDTreeMapOpenVSplit=''
let g:NERDTreeMapOpenInTab=''
" Start NERDTree when Vim is started without file arguments.
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists('s:std_in') | NERDTree | endif
" If another buffer tries to replace NERDTree, put it in the other window, and bring back NERDTree.
autocmd BufEnter * if winnr() == winnr('h') && bufname('#') =~ 'NERD_tree_\d\+' && bufname('%') !~ 'NERD_tree_\d\+' && winnr('$') > 1 |
    \ let buf=bufnr() | buffer# | execute "normal! \<C-W>w" | execute 'buffer'.buf | endif


"
" Lists
"
autocmd FileType qf set nobuflisted
let g:quickfix_list_open = 0
let g:location_list_open = 0
let g:location_list_handler = 1
function! OpenList(pfx)
  if a:pfx == 'l'
    try
      lopen
      wincmd J
      8wincmd _
      wincmd p
      let g:location_list_open = 1
      let g:location_list_handler = 1
    catch /E776/
      echohl ErrorMsg
      echo "Location List is Empty."
      echohl None
      return
    endtry
  elseif a:pfx == 'c'
    copen
    wincmd K
    8wincmd _
    wincmd p
    let g:quickfix_list_open = 1
  endif
endfunction

function! ToggleList(pfx)
  if a:pfx == 'l'
    if g:location_list_open
      let g:location_list_open = 0
      let g:location_list_handler = 0
      lclose
    else
      call OpenList(a:pfx)
    endif
  elseif a:pfx == 'c'
    if g:quickfix_list_open
      let g:quickfix_list_open = 0
      cclose
    else
      call OpenList(a:pfx)
    endif
  endif
endfunction

function! CloseBuf()
  cclose
  let g:location_list_open = 0
  lclose
  bdelete
endfunction

autocmd BufWinEnter * if g:quickfix_list_open && &modifiable | call OpenList('c') | endif

function! LocationListHandler()
  if &modifiable && g:location_list_handler
    let l:is_empty = empty(getloclist(0))
    if !l:is_empty
      call OpenList('l')
    else
      let g:location_list_open = 0
      lclose
    endif
  endif
endfunction
autocmd CursorHold,CursorHoldI * call LocationListHandler()

function! CycleList(type)
  if a:type ==# 'c'
    try
      cnext
    catch /E553/
      cc 1
    catch /E42/
      echohl ErrorMsg
      echo "Quickfix List is Empty."
      echohl None
      return
    endtry
  elseif a:type ==# 'l'
    try
      lafter
    catch /E553/
      ll 1
    catch /E42/
      echohl ErrorMsg
      echo "Location List is Empty."
      echohl None
      return
    endtry
  endif
endfunction

"
" Colours
"
if filereadable(expand("$HOME/.config/tinted-theming/set_theme.vim"))
	let base16_colorspace=256
	let base16colorspace=256
	let tinted_colorspace=256
	source $HOME/.config/tinted-theming/set_theme.vim
endif


"
" Airline
"
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#ycm#enabled = 1
let g:airline_section_y = ''
let g:airline_section_z = '%p%% %l/%L %v'


"
" YCM
"
function! AfterYcm()
  wincmd p
  call OpenList('c')
endfunction
let g:ycm_autoclose_preview_window_after_completion = 1
" Auto location list
let g:ycm_always_populate_location_list = 1

"
" Folding
"
set foldmethod=syntax
autocmd BufWinLeave *.* mkview
autocmd BufWinEnter *.* silent loadview
autocmd FileType python setlocal foldmethod=indent
" Don't screw up folds when inserting text that might affect them, until
" leaving insert mode. Foldmethod is local to the window. Protect against
" screwing up folding when switching between windows.
autocmd InsertEnter * if !exists('w:last_fdm') | let w:last_fdm=&foldmethod | setlocal foldmethod=manual | endif
autocmd InsertLeave,WinLeave * if exists('w:last_fdm') | let &l:foldmethod=w:last_fdm | unlet w:last_fdm | endif


"
" Mapping
"  
noremap a h
noremap A ^
noremap t k
noremap T H
noremap s j
noremap S L
noremap e l
noremap E $
noremap f n
noremap F N
noremap n a
noremap N A
noremap j J
" Cursor
map <leader><Left> <C-w>h
imap <leader><Left> <C-w>h
map <leader><Right> <C-w>l
imap <leader><Right> <C-w>l
map <leader><Up> <C-w>k
imap <leader><Up> <C-w>k
map <leader><Down> <C-w>j
imap <leader><Down> <C-w>j
map <PageUp> <C-b>
map <PageDown> <C-f>
" Window
map <leader>q :wqall<CR>
imap <leader>q <C-[>:wqall<CR>
map <leader>w :w<CR>
imap <leader>w <C-o>:w<CR>
map <leader>C <C-w>c
imap <leader>C <C-w>c
map <leader>Z :vsplit<CR>
imap <leader>Z <C-o>:vsplit<CR>
map <leader>z :split<CR>
imap <leader>z <C-o>:split<CR>
" Buffer
map <leader>c :call CloseBuf()<CR>
imap <leader>c <C-[>:call CloseBuf()<CR>
map <leader>a :bprevious<CR>
imap <leader>a <C-o>:bprevious<CR>
map <leader>e :bnext<CR>
imap <leader>e <C-o>:bnext<CR>
" Sizing
map <leader>+ <C-w>5+
imap <leader>+ <C-w>5+
map <leader>- <C-w>5-
imap <leader>- <C-w>5-
map <leader>< <C-w>5<
imap <leader>< <C-w>5<
map <leader>> <C-w>5>
imap <leader>> <C-w>5>
map <leader>= <C-w>=
imap <leader>= <C-w>=
map <leader>_ <c-w>_
imap <leader>_ <c-w>_
map <leader>\| <c-w>\|
imap <leader>\| <c-w>\|
" Folding
map <leader>f za
imap <leader>f <C-o>za
map <leader>F zR
imap <leader>F <C-o>zR
" List
map <leader>s :call CycleList('c')<CR>
imap <leader>s :<C-o>call CycleList('c')<CR>
map <leader>t :call CycleList('l')<CR>
imap <leader>t :<C-o>call CycleList('l')<CR>
map <leader>S :call ToggleList('c')<CR>
imap <leader>S <C-o>:call ToggleList('c')<CR>
map <leader>T :call ToggleList('l')<CR>
imap <leader>T <C-o>:call ToggleList('l')<CR>
" YCM
map <leader>p :YcmCompleter GoToAlternateFile<CR>
imap <leader>p <C-o>:YcmCompleter GoToAlternateFile<CR>
map <leader>G :YcmCompleter GoToReferences<CR>:call AfterYcm()<CR>
imap <leader>G <C-o>:YcmCompleter GoToReferences<CR><C-o>:call AfterYcm()<CR>
map <leader>g :YcmCompleter GoTo<CR>
imap <leader>g <C-o>:YcmCompleter GoTo<CR>
map <leader>O <Plug>(YCMFindSymbolInWorkspace)
imap <leader>O <C-o><Plug>(YCMFindSymbolInWorkspace)
nmap <leader><Space> <plug>(YCMHover)
" Nerdtree
nmap <leader>o :NERDTreeToggle<CR>
let g:NERDTreeMenuUp='t'
let g:NERDTreeMenuDown='s'
let g:NERDTreeMapRefresh='a'
let g:NERDTreeMapCustomOpen='e'
" Etc
map <leader>m :noh<CR>
imap <leader>m <C-o>:noh<CR>
map <leader>u g;
imap <leader>u <C-o>g;
map <leader>U g,
imap <leader>U <C-o>g,
map <leader>b <C-o>
imap <leader>b <C-o><C-o>
map <leader>B <C-i>
imap <leader>B <C-o><C-i>
