# Description

`pygsc` is a Python script that lets you run shell scripts *interactively*. This is useful for doing live command line demos.

`pygsc` is a (another) rewrite of [`gsc`](https://github.com/CD3/gsc). There is a long history with the creation of this tool for a computer class I teach. You can read it
there.

## Features

- Run shell scripts interactively.
    - Characters are sent to the shell, on at a time, each time you press a key.
    - When the end of a line has been reached, press enter to go to the next line.
- Modal : switch between insert mode, command mode, and pass through mode (see below).
    - If you run into an error in your script (a typo, or some file that is missing), you can switch to pass-through mode to quickly fix the error without
      exiting the demo.
- Statusline in the upper right corner of the terminal lets you know where you are and what mode your in. This can be disabled.

## Usage

To start a demo, run `gsc` with the script

```bash
$ gsc my_demo.sh
```

This will start shell (by default, `$SHELL`) in a forked process and connect to it with a psuedo terminal. Each line in the script
is then loaded and sent to the shell, on character at a time, while the user types. Once the entire line has been sent, `gsc` waits
for the user to press return, and the next line is loaded.

You can specify a different shell with the `--shell` option.

```bash
$ gsc my_demo.sh --shell zsh
```



### Keybindings

#### Insert Mode

Insert mode is the main mode, `gsc` starts up in insert mode. While in insert mode, `gsc` will read each line of the script and send
characters to the shell each time the user presses a key. When an entire line has been sent to the shell, `gsc` will wait for the user
to press enter before starting the next line in the script.

`<any character>`: send next character to shell.

`return`: if at the end of current script line send `\r` and load next script line. otherwise, send next character.

`ctrl-d`: switch to command mode.

#### Insert Mode

Line mode is special type of insert mode where entire lines are sent to the shell instead of single characters. This mode is useful for
quickly testing a script.

`return`: send `\r` and load next script line.

`ctrl-d`: switch to command mode.

#### Command Mode

Command mode allows the user to make (simple) adjustments during the demo. The user can move the current character position, for example
to skip a line or backup.

`i`: switch to insert mode.

`I`: switch to line mode.

`p`: switch to pass-through mode.

`j`: jump to the next line in the script.

`k`: jump to the previous line in the script.

`h`: jump to the previous character in the current script line.

`k`: jump to the next character in the current script line.

`^`: jump to the first character in the current script line.

`$`: jump to the end of the current script line (one past the last character).

`s`: toggle status line on/off.

#### Pass-through Mode

Pass-through mode sends all user input to the shell. This can be used to fix the current line, fix the environment (remove files that are not supposed to be there),
or just temporarily take over the demo.

`ctrl-d`: switch to command mode.
