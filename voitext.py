"""Voitext

Usage:
    voitext [-l <str>] [-d] [-f <int>] [-n <int>] [-m] [-s <int>] [-b <str>] <file>
    voitext edit
    voitext split
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
"""

import os
import re
import textwrap
from enum import Enum
from typing import List, Dict, Any, Tuple, Callable

import speech_recognition as sr
import yaml
from PIL import Image, ImageDraw, ImageFont
from docopt import docopt
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, CompositeVideoClip
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent

CWD_PATH: str = os.getcwd()
OUTPUT_PATH: str = os.path.join(CWD_PATH, "output")
FONT_FILE: str = os.path.join(CWD_PATH, "font.ttf")
VERSION: float = 0.1

class BG_COLOR(Enum):
    GREEN = (0, 177, 64)
    BLUE = (0, 71, 187)
    BLACK = (0, 0, 0)


def __check_path_exists(path: str) -> bool:
    if os.path.exists(path):
        return True
    return False


class Voitext:
    VIDEO: int = 0
    AUDIO: int = 1
    IMAGE: int = 2
    OUTPUT: int = 3
    TEXT: int = 4
    YAML: int = 5
    DURATION: int = 6
    DURATION_RANGE: int = 7

    ext: Dict[int, str] = {
        VIDEO: ".webm",
        AUDIO: ".wav",
        IMAGE: ".png",
        YAML: ".yaml"
    }

    media_name: Dict[int, str] = {
        VIDEO: "video",
        AUDIO: "audio",
        IMAGE: "image",
        TEXT: "text",
        DURATION: "duration",
        DURATION_RANGE: "range"
    }

    media_dir_name: Dict[int, str] = {
        VIDEO: "videos",
        AUDIO: "sounds",
        IMAGE: "images",
    }

    def __init__(self, filename: str, fontsize: int = 24, video_bg_color=BG_COLOR.GREEN.name) -> None:
        self.__filename = filename
        self.__fontsize = fontsize
        self.__video_bg_color = self.set_bg_color(video_bg_color)

        self.__name: str = os.path.splitext(os.path.basename(self.__filename))[0]
        self.__output_data: Dict[int, str] = self.__create_output_dir()

        self.__check_media_type(self.__filename)

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def name(self) -> str:
        return self.__name

    @classmethod
    def __check_media_type(cls, filename: str) -> int:
        ext_ = os.path.splitext(filename)[1]
        for typ, ext in cls.ext.items():
            if ext.lower() == ext_.lower():
                return typ

        raise Exception(f"Extension used only: {', '.join(cls.ext.values())}")

    @classmethod
    def __split_audio(cls, filename: str, min_silence_len: int = None) -> Tuple[List[AudioSegment], List[List[int]]]:
        audio_segment: AudioSegment = AudioSegment.from_wav(filename)
        min_silence_len: int = min_silence_len if min_silence_len else 500
        silence_thresh: float = audio_segment.dBFS - 14

        chunk_list: List[AudioSegment] = split_on_silence(
            audio_segment=audio_segment,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=1000
        )

        split_range_list: List[List[int]] = detect_nonsilent(
            audio_segment=audio_segment,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
        )

        return chunk_list, split_range_list

    @staticmethod
    def set_bg_color(color: str) -> Tuple[int, int, int]:
        if color.upper() == BG_COLOR.GREEN.name:
            return BG_COLOR.GREEN.value
        elif color.upper() == BG_COLOR.GREEN.name:
            return BG_COLOR.BLUE.value

        return BG_COLOR.BLACK.value

    @staticmethod
    def __text_to_image(output_filename: str, text: str, fontsize: int) -> str:
        font: ImageFont.FreeTypeFont = ImageFont.truetype(
            font=FONT_FILE,
            size=fontsize
        )

        image_h: int = 0
        text_lines: List[str] = textwrap.wrap(text, width=40)

        for txt_line in text_lines:
            image_h += int(font.getsize(txt_line)[1])

        image_w, image_h = [1920, int(image_h + (fontsize * 0.21))]

        image: Image = Image.new(
            mode="RGBA",
            size=(image_w, image_h),
            color=(0, 0, 0, 0)
        )

        draw: ImageDraw = ImageDraw.Draw(image)

        t_h: int = 0
        for txt_line in text_lines:
            tx_w, tx_h = font.getsize(txt_line)
            draw.text(
                xy=((image_w - tx_w) / 2, t_h),
                text=txt_line,
                font=font,
                fill="white",
            )
            t_h += tx_h

        image.save(output_filename)

        return output_filename

    @staticmethod
    def __voice_to_text(audio_file: str, language: str = None) -> str:
        rec: sr.Recognizer = sr.Recognizer()
        text: str = "..."

        with sr.AudioFile(audio_file) as source:
            audio_listened: sr.AudioData = rec.listen(source)
            try:
                text: Any = rec.recognize_google(
                    audio_data=audio_listened,
                    language=language if language else "id-ID"
                )
                print(text)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service\n{e}")
            finally:
                print(os.path.basename(audio_file), ":", text)
                return text

    @staticmethod
    def __media_to_video(output_filename: str, image_file: str, video_bg_color: Tuple[int, int, int], duration: float,
                         audio_file: str = None, fps: int = 30) -> str:
        image_clip: ImageClip = ImageClip(
            img=image_file,
            duration=duration
        )

        if audio_file:
            audio_clip: AudioFileClip = AudioFileClip(audio_file)
            image_clip = image_clip.set_audio(audio_clip)

        final_clip: CompositeVideoClip = CompositeVideoClip([image_clip], bg_color=video_bg_color)
        final_clip.write_videofile(output_filename, fps=fps)
        final_clip.close()

        return output_filename

    @staticmethod
    def __extract_audio(filename: str, output_filename: str) -> str:
        video_clip: VideoFileClip = VideoFileClip(
            filename=filename
        )

        audio_clip: AudioFileClip = video_clip.audio

        audio_clip.write_audiofile(filename=output_filename)

        return output_filename

    @staticmethod
    def export_from_data(filename: str, number: int, fontsize: int, video_bg_color: str = BG_COLOR.GREEN.name,
                         mute_video: bool = False) -> None:
        with open(filename, "r") as f:
            data: Dict[int, Dict[str, Any]] = yaml.load(f)

        data_list: List[Dict[str, Any]] = [d for d in data.values()]
        data_list = [data_list[number - 1]] if number else data_list

        for dt in data_list:
            video_file: str = dt.get(Voitext.media_name.get(Voitext.VIDEO))
            audio_file: str = dt.get(Voitext.media_name.get(Voitext.AUDIO))
            image_file: str = dt.get(Voitext.media_name.get(Voitext.IMAGE))
            text: str = dt.get(Voitext.media_name.get(Voitext.TEXT))
            duration: float = dt.get(Voitext.media_name.get(Voitext.DURATION))

            Voitext.__text_to_image(
                output_filename=image_file,
                text=text,
                fontsize=fontsize
            )
            Voitext.__media_to_video(
                output_filename=video_file,
                image_file=image_file,
                video_bg_color=Voitext.set_bg_color(video_bg_color),
                duration=duration,
                audio_file=audio_file if not mute_video else None
            )

    # TODO: test split on word from speech
    @staticmethod
    def split_one_word(filename: str, fontsize: int, video_bg_color: str = BG_COLOR.GREEN.name) -> None:
        with open(filename, "r") as f:
            data: Dict[int, Dict[str, Any]] = yaml.load(f)

        edit_path: Callable[[str, str], str] = lambda filename, name: os.path.join(os.path.dirname(filename),
                                                                                   f"split_{name}")
        # edit_filename

        for i, dt in enumerate(data.values(), start=1):
            video_path: str = edit_path(dt.get(Voitext.media_name.get(Voitext.VIDEO)),
                                        f"{Voitext.media_name[Voitext.VIDEO]}{i}")
            image_path: str = edit_path(dt.get(Voitext.media_name.get(Voitext.IMAGE)),
                                        f"{Voitext.media_name[Voitext.IMAGE]}{i}")
            text: str = dt.get(Voitext.media_name.get(Voitext.TEXT))
            duration: float = dt.get(Voitext.media_name.get(Voitext.DURATION))
            text_list: List[str] = textwrap.wrap(text, width=1, break_long_words=False)
            d = duration / len(text_list)

            for p in (video_path, image_path):
                if not os.path.exists(p):
                    os.makedirs(p)

            for i, t in enumerate(text_list, start=1):
                image_file: str = os.path.join(image_path, f"{i}.{t}{Voitext.ext.get(Voitext.IMAGE)}")
                video_file: str = os.path.join(video_path, f"{i}.{t}{Voitext.ext.get(Voitext.VIDEO)}")

                Voitext.__text_to_image(
                    output_filename=image_file,
                    text=t.upper(),
                    fontsize=fontsize
                )

                Voitext.__media_to_video(
                    output_filename=video_file,
                    image_file=image_file,
                    video_bg_color=Voitext.set_bg_color(video_bg_color),
                    duration=d,
                )

    def __create_output_dir(self) -> Dict[int, str]:
        version = 1
        dir_list: List[str] = [d for d in os.listdir(OUTPUT_PATH) if os.path.isdir(os.path.join(OUTPUT_PATH, d))]

        for d in dir_list:
            match = re.match(r"{0}\d+".format(self.__name), d, re.IGNORECASE)
            if match:
                version += 1
        output_path: str = os.path.join(OUTPUT_PATH, f"{self.__name}{version}")
        output_data: Dict[int, str] = {
            self.OUTPUT: output_path
        }

        if not os.path.exists(output_path):
            os.makedirs(output_path)
            for k, v in self.media_dir_name.items():
                media_dir_path: str = os.path.join(output_path, v)
                os.makedirs(media_dir_path)
                output_data[k] = media_dir_path

        return output_data

    def __create_data(self, data_name: str, data_dict: Dict[int, Dict[str, Any]]) -> None:
        yaml_name: str = f"{data_name}{self.ext[self.YAML]}"
        yaml_file: str = os.path.join(self.__output_data[self.OUTPUT], yaml_name)
        with open(yaml_file, "w") as f:
            yaml.dump(data_dict, f)

    def export(self, language: str = None, min_silence_len: int = 500, mute_video: bool = False) -> None:
        text_list: List[str] = []
        duration_list: List[float] = []
        audio_file_list: List[str] = []
        image_file_list: List[str] = []
        video_file_list: List[str] = []
        enum_start: int = 1

        audio_name: str = f"{self.__name}{self.ext[self.AUDIO]}"
        audio_file: str = os.path.join(self.__output_data[self.OUTPUT], audio_name)
        filename = self.__extract_audio(self.__filename, audio_file) if self.__check_media_type(
            self.__filename) == self.VIDEO else self.__filename

        audio_chunk_list, duration_range_list = self.__split_audio(
            filename=filename,
            min_silence_len=min_silence_len
        )

        for i, audio_chunk in enumerate(audio_chunk_list, start=enum_start):
            audio_chunk: AudioSegment
            chunk_name: str = f"{self.media_name[self.AUDIO]}{i}{self.ext[self.AUDIO]}"
            chunk_file: str = os.path.join(self.__output_data[self.AUDIO], chunk_name)
            audio_chunk.export(chunk_file, format=self.ext[self.AUDIO].replace(".", ""))
            audio_file_list.append(chunk_file)
            duration_list.append(audio_chunk.duration_seconds)

            text: str = self.__voice_to_text(
                audio_file=chunk_file,
                language=language
            )
            text_list.append(text)

        for i, text in enumerate(text_list, start=enum_start):
            image_name: str = f"{self.media_name[self.IMAGE]}{i}{self.ext[self.IMAGE]}"
            image_file: str = os.path.join(self.__output_data[self.IMAGE], image_name)
            self.__text_to_image(
                output_filename=image_file,
                text=text.upper(),
                fontsize=self.__fontsize
            )

            image_file_list.append(image_file)

        data_dict: Dict[int, Dict[str, Any]] = {}

        for i, (text, image_file, audio_file, duration, duration_range) in enumerate(
                zip(text_list, image_file_list, audio_file_list, duration_list, duration_range_list),
                start=enum_start):
            video_name: str = f"{self.media_name[self.VIDEO]}{i}{self.ext[self.VIDEO]}"
            video_file: str = os.path.join(self.__output_data[self.VIDEO], video_name)
            self.__media_to_video(
                output_filename=video_file,
                image_file=image_file,
                video_bg_color=self.__video_bg_color,
                duration=duration,
                audio_file=audio_file if not mute_video else None
            )

            video_file_list.append(video_file)

            data_dict[i] = {
                self.media_name[self.VIDEO]: video_file,
                self.media_name[self.AUDIO]: audio_file,
                self.media_name[self.IMAGE]: image_file,
                self.media_name[self.TEXT]: text,
                self.media_name[self.DURATION]: duration,
                self.media_name[self.DURATION_RANGE]: duration_range
            }

        self.__create_data(self.__name, data_dict)
        print("Done.")


if __name__ == "__main__":
    arguments = docopt(__doc__, version=f"Voitext v{VERSION}")

    file = arguments["<file>"]
    data = arguments["--data"]
    fontsize = arguments["--fontsize"]
    number = arguments["--number"]
    mute = arguments["--mute"]
    lang = arguments["--lang"]
    min_silence_len = arguments["--min-silence-len"]
    bg_color = arguments["--bg-color"]

    _, ext = os.path.splitext(file)
    video_formats: List[str] = [
        Voitext.ext[Voitext.AUDIO],
        Voitext.ext[Voitext.VIDEO]
    ]
    fontsize = fontsize if fontsize else 48
    min_silence_len = min_silence_len if min_silence_len else 500
    number = int(number) if number else 0
    bg_color = bg_color if bg_color else BG_COLOR.GREEN.name

    if ext.lower() in video_formats:
        voitext: Voitext = Voitext(file, fontsize=fontsize)
        voitext.export(
            language=lang,
            min_silence_len=min_silence_len,
            mute_video=bool(mute)
        )
    elif data and ext.lower() == Voitext.ext[Voitext.YAML]:
        Voitext.export_from_data(
            filename=file,
            number=number,
            fontsize=fontsize,
            video_bg_color=bg_color,
            mute_video=bool(mute)
        )
    else:
        raise Exception(f"{ext} media format not available.")
