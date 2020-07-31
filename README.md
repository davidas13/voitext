# voitext

*Default width for text 1920

### How to install
- git clone https://github.com/wongselent/voitext.git
- cd voitext/
- pipenv install
- pipenv run dev "example_video.webm"


```bash
Usage:
    voitext [-l <str>] [-d] [-f <int>] [-n <int>] [-m] [-s <int>] [-b <str>] <file>
    voitext (-h | --help)
    voitext --version

Options:
    -h --help                           Show this screen.
    --version                           Show version.
    -d --data                           Export from yaml data.
    -m --mute                           Export video without sound.
    -l <lang>, --lang <str>             Language type speech. default "id-ID"
    -f <int>, --fontsize <int>          Font Size text in video. default: 48
    -n <int>, --number <int>            Data position from the data file list, if 0 then all the list in the data file will be exported. default: 0
    -s <int> --min-silence-len <int>    Minimum length of a silence to be used for a split. default: 500
    -b <str> --bg-color <str>           Set BG Color. Default: "green"
```
