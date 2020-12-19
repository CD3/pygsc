# pause: -1
# display: "Characters are sent to the shell one at a time as you type."
ls
# display: "To load a new line, press return."
# pause: -1
# display: "Command line apps with their own prompt can be scripted too."
gnuplot
plot sin(x)
exit
# display: "Even full screen terminal apps work."
vim demo.txt

aterminal applications like vim, gnuplot,
even remote ssh connections, can all be scripted.

:wq
# display: ""
ls
cat demo.txt
rm demo.txt
ls
echo "happy demoing!"

