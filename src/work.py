import os
from pydub import AudioSegment

def merge_audios(file_list, output_name):
    combined = AudioSegment.empty()
    
    for file in file_list:
        if not os.path.exists(file):
            print(f"警告：找不到文件 {file}，请检查路径！")
            continue
            
        print(f"正在处理：{file} ...")
        # 读取音频并追加到总音频中
        audio = AudioSegment.from_file(file)
        combined += audio
        
    # 导出合并后的文件
    print(f"正在导出合并文件：{output_name} ...")
    # 可以在这里指定比特率，保证音质
    combined.export(output_name, format="mp3", bitrate="192k") 
    print("✅ 合并完成！")

if __name__ == "__main__":
    # 把你的6个文件名按顺序写在这里（最好和脚本放在同一个文件夹）
    audio_files = [
        "1.mp3", 
        "2.mp3", 
        "3.mp3", 
        "4.mp3", 
        "5.mp3", 
        "6.mp3"
    ]
    
    output_filename = "final_english_listening.mp3"
    merge_audios(audio_files, output_filename)