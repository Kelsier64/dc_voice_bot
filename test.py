from gpt_sovits_python import TTS, TTS_Config  # 根据需要调整导入
import soundfile as sf
import nltk
nltk.download('averaged_perceptron_tagger_eng')
config_dict = {
    "default": {
        "device": "cuda",
        "is_half": True,
        "t2s_weights_path": "/home/kelsier/py/dc_bot/models/gpt.ckpt",
        "vits_weights_path": "/home/kelsier/py/dc_bot/models/sovits.pth",
        "cnhuhbert_base_path": "/home/kelsier/py/dc_bot/models/chinese-hubert-base",
        "bert_base_path": "/home/kelsier/py/dc_bot/models/chinese-roberta-wwm-ext-large",
    }
}
tts_config = TTS_Config(config_dict)
tts_pipeline = TTS(tts_config)

params = {
    "text": "一看我妈天天在家里面全职家庭主妇，不是洗衣服就是做饭，躺赢狗。",
    "text_lang": "zh",
    "ref_audio_path": "/home/kelsier/py/dc_bot/mvp.wav",
}

sr, audio_data = next(tts_pipeline.run(params))

sf.write("test.wav", audio_data, sr)