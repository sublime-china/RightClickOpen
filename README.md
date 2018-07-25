# Right click open


This is a right-click package for **sublime text 3**, it contains four features:

* Open a `url` in browser.
* `Open file` in sublime, if the file is existed on the computer.
* `Browse` files existed in your computer.
* Select a sentence, search it on`baidu` or ` google`.

It is can recognize the following lines with its type and intelligently decide show it on `context menu` or not.

Some test:

```
D:\SublimeText3\Data\Packages\right click open\print.ss

D:\SublimeText3\Data\Packages\right click open

right_click_here.py

print.ss

..

..\right click open

..\right click open\open_test.txt

..\right click open\right_click_here.py

https://www.baidu.com

```

Bugs:

If you try to right-click a file is not saved on your computer,
will trigger a FileNotFoundError error!
