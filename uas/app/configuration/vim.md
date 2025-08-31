# 📝 Vim Beginner Cheat Sheet

## 🔑 Modes

- **Normal mode** (default): Move around, delete, copy, paste, etc.
- **Insert mode**: Type text. (`i` to enter, `Esc` to exit)
- **Visual mode**: Select text. (`v`)
- **Command mode**: Run commands. (`:`)

---

## 🏃 Moving around

- `h` → left
- `l` → right
- `j` → down
- `k` → up
- `0` → beginning of line
- `^` → first non-space character
- `$` → end of line
- `w` → next word
- `e` → end of word
- `b` → back to beginning of word
- `gg` → go to top of file
- `G` → go to bottom of file
- `:n` → go to line `n` (e.g. `:42` jumps to line 42)

---

## ✍️ Insert text

- `i` → insert before cursor
- `a` → insert after cursor
- `o` → new line below
- `O` → new line above
- `I` → insert at beginning of line
- `A` → insert at end of line

---

## 🗑️ Delete

- `x` → delete character under cursor
- `dw` → delete word
- `dd` → delete whole line
- `d$` → delete to end of line
- `d0` → delete to beginning of line

---

## 📋 Copy & Paste

- `yy` → copy (yank) line
- `yw` → yank word
- `p` → paste after cursor
- `P` → paste before cursor

---

## 🔄 Undo & Redo

- `u` → undo
- `Ctrl + r` → redo

---

## 🔍 Search

- `/word` → search forward for “word”
- `?word` → search backward for “word”
- `n` → next match
- `N` → previous match

---

## 💾 Save & Quit

- `:w` → save
- `:q` → quit
- `:wq` → save and quit
- `:q!` → quit without saving
