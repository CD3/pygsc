echo "Characters are sent to the shell one at a time as you type. To load a new line, press return."
ls
vim demo.txt

aterminal applications like vim, gnuplot,
even remote ssh connections can all be scripted.

:wq
ls
cat demo.txt
rm demo.txt
ls
gnuplot
plot sin(x)
exit
echo "happy demoing!"

