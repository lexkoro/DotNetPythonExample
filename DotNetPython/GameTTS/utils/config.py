from pathlib import Path

#######################
#    INITIAL PATHS    #
#######################
class PATHS:
    APP_FOLDER = Path(Path(__name__).parent.resolve(), "GameTTS")
    TTS_CONFIG_PATH = Path(APP_FOLDER, "vits/model/", "config.json")
    TTS_MODEL_PATH = Path(APP_FOLDER, "vits/model/", "G_900000.pth")
    LOGGING_PATH = Path(APP_FOLDER, "log/", "debug.log")


#######################
#     APP SETTINGS    #
#######################
class APP_SETTINGS:
    EXPORT_FILE_ENABLED = False
    EXPORT_FILE_PATH = ""
    EXPORT_FILE_EXT = "wav"


#######################
#  SPEECH SETTINGS    #
#######################
class SPEECH_SETTINGS:
    SPEECH_SPEED = 1.1
    SPEECH_VAR_A = 0.345
    SPEECH_VAR_B = 0.4
