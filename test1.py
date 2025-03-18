import re
import os
import asyncio
import soundfile as sf
from pydub import AudioSegment
from gpt_sovits_python import TTS, TTS_Config

def split_string_by_keywords(text, keyword_dict):
    # 提取關鍵字
    keywords = [item for sublist in keyword_dict.values() for item in sublist]  # 展平字典的值
    # 使用正則表達式找到所有關鍵字，並拆分字串
    pattern = f"({'|'.join(map(re.escape, keywords))})"
    result = re.split(pattern, text)
    # 過濾掉空字串
    return [keyword_dict.get(s, s) for s in result if s]

async def gpt_sovits(text: str, out_file="speech.wav"):
    config_dict = {
        "default": {
            "device": "cuda",
            "is_half": True,
            "t2s_weights_path": "models/gpt.ckpt",
            "vits_weights_path": "models/sovits.pth",
            "cnhuhbert_base_path": "models/chinese-hubert-base",
            "bert_base_path": "models/chinese-roberta-wwm-ext-large",
        }
    }
    
    tts_config = TTS_Config(config_dict)
    tts_pipeline = TTS(tts_config)

    params = {
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": "ref.wav",
        "top_k": 5,
        "text_split_method": "cut2",
    }

    sr, audio_data = next(tts_pipeline.run(params))
    sf.write(out_file, audio_data, sr)

# async def main():
#     # 測試文字及關鍵字字典
#     text = "啊哈哈哈沙士比亞我爸得了mvp"
#     keyword_dict = {
#     "mvp": ["mvp"],
#     "啊哈哈哈":["ahhaha"],
#     "沙士比亞":["kill"]
# }
#     output = split_string_by_keywords(text, keyword_dict)
#     print("拆分結果:", output)  # 例如：['我爸得了', 'mvp']

#     combined = AudioSegment.empty()
    
#     for idx, part in enumerate(output):
#         # 如果為字串則使用 gpt_sovits 生成 wav
#         if isinstance(part, str):
#             temp_wav = f"temp_{idx}.wav"
#             await gpt_sovits(part, out_file=temp_wav)
#             seg_audio = AudioSegment.from_file(temp_wav, format="wav")
#             combined += seg_audio
#         # 如果為列表則從 sounds 資料夾讀取對應的 wav
#         elif isinstance(part, list):
#             # 假設列表的第一個元素為檔名（不含副檔名）
#             wav_path = os.path.join("sounds", f"{part[0]}.wav")
#             seg_audio = AudioSegment.from_file(wav_path, format="wav")
#             combined += seg_audio

#     combined.export("final.wav", format="wav")
#     print("合併後 wav 已輸出為 final.wav")

# if __name__ == '__main__':
#     asyncio.run(main())

text = "啊哈哈哈沙士比亞我爸得了mvp"
keyword_dict = {
"mvp": ["mvp"],
"啊哈哈哈":["ahhaha"],
"沙士比亞":["kill"]
}
output = split_string_by_keywords(text, keyword_dict)
print(output)