# README

## 关于代码

- 本代码为爬取`百度汉字`内收录的所有`unicode`汉字及其所成所有词的爬虫代码。

## 如何使用

``` 
.
├── README.md
├── data
│   ├── IPpool.json
└── src
    ├── char.py
    └── word.py
```

代码在`src/`下，分为`word.py`和`char.py`。在`src/`目录下：

- 使用`python word.py`，在输入需要爬取的`unicode` 汉字的范围后，即可实现对这个范围内所有的汉字所成的词的爬取，得到的数据文件以json形式存储在`data/`下。默认情况下，只对每个字的所成词的第一页进行爬取，若要爬取所有的词，在`word.py`下对`getWordList`调用的地方将`getWordList(char, IPs)`改为`getWordList(char, IPs, one_page=False)`，只需要在`if name == '__main__':`下修改一处即可。

- 使用`python char.py`，在输入需要爬取的`unicode` 汉字的范围后，即可实现对这个范围内所有汉字的爬取，得到的数据文件以json形式存储在`data/`下。

- 本代码使用了IP代理，请将代理使用的IP以如下`json`的格式存于`data/`下，命名为`IpPool.json`：

  ``` json
  {"data":
   [{"ip":"0.0.0.0","port":1111},
    ...
   ]
  }
  ```

  