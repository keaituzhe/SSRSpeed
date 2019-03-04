

# SSRSpeed
ShadowsocksR 批量测速工具

## 特点

 - Support SpeedTestNet, Fast.com,Cachefly and socket(removed).
 - 支持 Speedtestnet，Fast.com，Cachefly测速（原始Socket已移除）
 - 支持导出结果为 json 和 png
 - 支持从ShadowsocksR-CSharp的配置文件（gui-config.json）导入或者从订阅链接导入（确认支持SSPanelv2,v3）
 - 支持从导出的json文件再次导入并导出为指定格式

## 依赖

 - Python >= 3.6
 - pillow
 - requests
 - pysocks


## 快速上手

    pip install -r requirements.txt
    或者
    pip3 install -r requirements.txt

    python .\main.py
    Usage: main.py [options] arg1 arg2...

    Options:
      --version             显示版本号然后退出程序
      -h, --help            显示该帮助并退出
      --cli					以内置命令行形式运行程序
      -c GUICONFIG, --config=GUICONFIG
                        从ShadowsocksR的配置文件中导入节点
      -u URL, --url=URL     从订阅链接中导入节点
      -m TEST_METHOD, --method=TEST_METHOD
                        选择测速方式，当前支持speedtestnet,fast和cachefly
      -f FILTER, --filter=FILTER
	                    仅选中组名或者备注中包含该关键字的节点
      --fr=REMARKS, --fremark=REMARKS
                        仅选中备注中包含该关键字的节点
      --fg=GROUP, --fgroup=GROUP
                        仅选中组名中包含该关键字的节点
      -y, --yes             跳过节点信息确认直接进行测试
      -e EXPORT_FILE_TYPE, --export=EXPORT_FILE_TYPE
                        设置导出文件格式，当前支持json和png
      -i IMPORT_FILE, --import=IMPORT_FILE
                        从导出文件中导入结果，仅支持json
      --debug               以调试模式运行程序

示例用法 :
 - python main.py  -c gui-config.json  -f 韩国 --fr Azure --fg MoCloudPlus -e json -m fast
 - python main.py -u https://mocloudplus.com/link/ABCDEFG123456?mu=0 -f 韩国 --fr Azure --fg MoCloudPlus -e png -m fast

内置命令行用法(python main.py --cli):

    type 'h' for help.
    > h
    [][INFO][9196][shell.py:24]Show Console Help.
    Options:
            h
                     Show this message.
            c CONFIG_FILE
                     Import shadowsocksr config from config file.
            u URL
                     Import shadowsocksr config from subscription link.
            m METHOD
                     Select test medhod in speedtestnet,fast and cachefly.
            f KEYWORD
                     Filter nodes by group and remarks using keyword.
            fr KEYWORD
                     Filter nodes by remarks using keyword.
            fg KEYWORD
                     Filter nodes by group using keyword.
            l
                     Show nodes in the list.
            e
                     Start test.
            e TYPE
                     Export test result to json or png file,now supported 'png' or 'json'
            i FILENAME
                     Import test result from json file and export it.
            q
                     Exit.
    
    > c gui-config.json
    [][INFO][9196][shadowsocksR.py:172]Read 468 node(s)
    > m fast
    [][INFO][9196][shell.py:65]Test method set : FAST
    > f MoCloudPlus
    > f IDCF
    > fr 543
    > l
    [][INFO][9196][shadowsocksR.py:134]MoCloudPlus - 单端口多用户 - 日本-3-IDCF-等级2-倍率3 - 543 端 口单端口多用户
    > t
    
    Testing info....
    
    > e png
    [][INFO][9196][exportResult.py:78]Result image saved as XXXX.png
    > e json
    [][INFO][9196][exportResult.py:107]Result exported as XXXX.json
    > q

内置命令行翻译如下：

    Options:
                h
                         显示帮助
                c CONFIG_FILE
                         从shadowsocksr-csharp的配置文件中导入节点
                u URL
                         从订阅链接中导入节点
                m METHOD
                         选择测试方式，当前支持speedtestnet,fast,cachefly
                f KEYWORD
                         过滤出组名和备注中含有关键字的节点
                fr KEYWORD
                         过滤出备注中含有关键字的节点
                fg KEYWORD
                         过滤出组名中含有关键字的节点
                l
                         显示当前待测试的节点
                e
                         开始测试
                e TYPE
                         导出测试数据，当前支持 png 和 json 格式
                i FILENAME
                         从json格式的导出数据中导入测试数据
                q
                         Goodbye

关键字优先级如下
>  -i > -c > -u
>  当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，三个参数中优先级最大的被采用，其余将会被忽略
>  
>  -f > --fg > --fr
>  当以上三个参数中多于一个被使用时，参数的采用顺序如上所示，将从优先级最大的参数开始过滤，如当同时采用-f --fg --fr时，将优先使用-f参数过滤节点，其次时--fg，最后为--fr


## 开发者

 - 初始版本 [@ranwen](https://github.com/ranwen)

## 感谢
 - [speedtest-cli](https://github.com/sivel/speedtest-cli)
 - [Fast.com-cli](https://github.com/nkgilley/fast.com)
