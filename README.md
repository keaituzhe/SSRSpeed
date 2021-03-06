


# SSRSpeed
ShadowsocksR Batch Speed Tool

中文文档请查看 [Readme_ZH_CN](https://github.com/NyanChanMeow/SSRSpeed/blob/master/README_ZH_CN.md)

## Features

 - Support SpeedTestNet, Fast.com,Cachefly and socket(removed).
 - Support for exporting result as json and png.
 - Support batch import of SSR configuration from ShadowsocksR-CSharp configuration file and SSPanel-v2, v3 subscription link.
 - Support for importing data from any Json export file and re-exporting files of the specified format.

## Requirements

 - Python >= 3.6
 - pillow
 - requests
 - pysocks


## Getting started

    pip install -r requirements.txt
    or
    pip3 install -r requirements.txt

    python .\main.py
    Usage: main.py [options] arg1 arg2...
    
    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -c GUICONFIG, --config=GUICONFIG
                            Load config generated by shadowsocksr-csharp.
      -u URL, --url=URL     Load ssr config from subscription url.
      -m TEST_METHOD, --method=TEST_METHOD
                            Select test method in
                            [speedtestnet,fast,cachefly,socket]
      --include=FILTER      Filter nodes by group and remarks using keyword.
      --include-remark=REMARKS
                            Filter nodes by remarks using keyword.
      --include-group=GROUP
                            Filter nodes by group name using keyword.
      --exclude=EFLITER     Exclude nodes by group and remarks using keyword.
      --exclude-group=EGFILTER
                            Exclude nodes by group using keyword.
      --exclude-remark=ERFILTER
                            Exclude nodes by remarks using keyword.
      -y, --yes             Skip node list confirmation before test.
      -e EXPORT_FILE_TYPE, --export=EXPORT_FILE_TYPE
                            Export test result to json or png file,now supported
                            'png' or 'json'
      -i IMPORT_FILE, --import=IMPORT_FILE
                            Import test result from json file and export it.
      --debug               Run program in debug mode.

Example usage :
 - python main.py  -c gui-config.json  --include 韩国 --include-remark Azure --include-group MoCloudPlus -e json -m fast
 - python main.py -u https://mocloudplus.com/link/ABCDEFG123456?mu=0 --include 香港 --include-remark Azure --include-group MoCloudPlus --exclude HKT -e png -m fast

The parameter priority is as follows: 
>  -i > -c > -u
>  The above sequence indicates that if the parameter has a higher priority, the parameter will be used first, and other parameters will be ignored.
>  
>  --include > --include-group > --include-remark
>   --exclude > --exclude-group > --exclude-remark
>  The above sequence indicates that node filtering will be performed in descending order of priority.

## Developers

 - Initial version [@ranwen](https://github.com/ranwen)

## Acknowledgement
 - [speedtest-cli](https://github.com/sivel/speedtest-cli)
 - [Fast.com-cli](https://github.com/nkgilley/fast.com)
