# CC-CEDICT to Yomichan converter

A Python script that converts the CC-CEDICT file to a Yomichan-supported dictionary file.

CC-CEDICT can be downloaded from here. https://www.mdbg.net/chinese/dictionary?page=cc-cedict

Yomichan is a pop-up dictionary. https://foosoft.net/projects/yomichan/

Although there exists already a CC-CEDICT (https://gist.github.com/shoui520/25460fd2e9fb194d3e5152fa2ce42ca2), it is not simplistic enough, for example pinyin can be seen twice. So, I created my own converter.

![Yomichan with 课 opened](img/1.png)

The converted dictionary has a new bullet point after classifiers (CL) because there usually is a new meaning after them. Other dictionaries usually lump everything into one line, which is not desirable.