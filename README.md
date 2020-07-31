# Voitext

### Cara Install dan menjalankannya
- downlaod file .zip di https://github.com/wongselent/voitext/releases
- unzip filde yang sudah terdownload:
    ```bash
    unzip voitext.zip -d "$PWD"/voitext
    ```
- siapkan sebuha video, kemudian jalankan:
    ```bash
    ./voitext "example_video.webm"
    ```
    
    **- atau -**
    
- install python 3
- install pipenv (tutorial ada disin: https://pipenv-fork.readthedocs.io/en/latest/install.html)
- clone project denga cara buka terminal, jalankan command:
    ```bash
    git clone https://github.com/wongselent/voitext.git
    ```
- masuk kedalam project folder:
    ```bash
    cd voitext/
    ```
- install semua packages, dengan cara:
    ```bash
    pipenv install
    ```
- siapkan sebuah video kemudian jalankan:
    ```bash
    pipenv run dev "example_video.webm"
    ```
### Catatan
- *Untuk mengganti style font lain, replace font.ttf*
- *Default width untuk hasil export 1920*

### Command
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

### Update kedepan
- mengexport setiap kata didalam video (example: https://www.youtube.com/watch?v=7kQJifNIa1U)
- membuat efek pada text (example: https://www.youtube.com/watch?v=XzXKXx2vfhk)
