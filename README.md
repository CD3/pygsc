# Description

`pygsc` is a Python script that lets you run shell scripts *interactively*. This is useful for doing live command line demos.

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

#### Command Mode

Command mode allows the user to make (simple) adjustments during the demo. The user can move the current character position, for example
to skip a line or backup.

`i`: switch to insert mode.

`p`: switch to pass-through mode.

`j`: jump to the next line in the script.

`k`: jump to the previous line in the script.

`h`: jump to the previous character in the current script line.

`k`: jump to the next character in the current script line.

`^`: jump to the first character in the current script line.

`$`: jump to the end of the current script line (one past the last character).

#### Pass-hhrough Mode

Pass-through mode sends all user input to the shell. This can be used to fix the current line, fix the environment (remove files that are not supposed to be there),
or just temporarily take over the demo.

`ctrl-d`: switch to command mode.
