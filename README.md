# pseudoRss

Expected usage is to specify blog article, news release, etc.
This script checks the specified sites and if there are new link, this scripts output the links.

Note that this script is basically expected to execute daily, etc. to enumerate new links on the specified site then we can get new article, etc.


## Requirements

```
pip install python-docx selenium
```


## How to use

```
usage: pseudoRss.py [-h] [-i INPUT] [-o OUTPUT] [-c CACHEDIR] [-s] [-t] [-d] [-n] [-f FORMAT] [PAGE ...]

Pseudo RSS

positional arguments:
  PAGE                  Web URLs (default: None)

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        list.csv url,title,sameDomain true or false,onlyTextExists true or false (default: .)
  -o OUTPUT, --output OUTPUT
                        Output filename (default: None)
  -c CACHEDIR, --cache CACHEDIR
                        Cache Dir (default: ~/.pseudoRss)
  -s, --sameDomain      Specify if you want to restrict in the same url (default: False)
  -t, --onlyTextExists  Specify if you want to restrict text existing link (default: False)
  -d, --diff            Specify if you want to list up new links (default: False)
  -n, --newOnlyDiff     Specify if you want to enumerate new one only (default: False)
  -f FORMAT, --format FORMAT
                        Set output format text or json or csv or docx (default: text)
```


### example1

```
$  python3 ./pseudoRss.py -s -t -d -n https://targetUrl.com/newsrelease/
```

### example2

```list.csv
https://targetUrl.com/newsroom/,News Release,True,True,True
https://targetUrl2.com/newsroom/,News Release2,True,True,True
```

```
$  python3 ./pseudoRss.py -s -t -c ~/temp -d -i list.csv -o summary.docx -f docx
```


