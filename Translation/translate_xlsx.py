import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def translate_text(text, target_language="en"):
    """翻译文本到目标语言"""
    # 跳过空文本
    if not text or text.strip() == "" or text.lower() == "nan":
        return text
    
    try:
        print(f"  Translating: {text[:50]}...")  # 显示正在翻译的内容前50个字符
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional translator. Output ONLY the translated text, without any explanations, notes, or original text."},
                {"role": "user",
                 "content": f"Translate this text to {target_language}. Output ONLY the translation, nothing else:\n\n{text}"}
            ],
            timeout=30  # 添加30秒超时
        )
        translation = completion.choices[0].message.content
        print(f"  ✓ Translated successfully")
        return translation.strip()
    except Exception as e:
        print(f"  ✗ Error during translation: {e}")
        return text


def Translate(input_file, output_file, target_language="en"):
    """翻译 Excel 文件中的所有内容"""
    try:
        print(f"Loading file: {input_file}")
        df = pd.read_excel(input_file, header=None)
        print(f"File loaded. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # 遍历每一列进行翻译
        for col_idx, column in enumerate(df.columns, 1):
            print(f"\n[{col_idx}/{len(df.columns)}] Translating column: '{column}'")
            
            # 逐行翻译，显示进度
            for row_idx in range(len(df)):
                cell_value = df.at[row_idx, column]
                
                # 跳过空值
                if pd.isna(cell_value) or str(cell_value).strip() == "":
                    continue
                
                print(f"  Row {row_idx + 1}/{len(df)}", end=" ")
                df.at[row_idx, column] = translate_text(str(cell_value), target_language)
                
                # 添加小延迟避免API限流
                time.sleep(0.2)

        print(f"\nSaving to: {output_path}")
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ Translation completed. Output saved to {output_file}")
        
    except FileNotFoundError:
        print(f"✗ Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"✗ Error processing the file: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置输入和输出文件路径

    # input_path = "chatlogAI.xlsx"
    # output_path = "chatlogAI_translated.xlsx"

    input_path = "chatlogHM.xlsx"
    output_path = "chatlogHM_translated.xlsx"

    print("=" * 60)
    print("Excel Translation Script")
    print("=" * 60)

    # 检查文件是否存在
    if not os.path.exists(input_path):
        print(f"✗ Error: File '{input_path}' not found in current directory.")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
    else:
        # 调用翻译函数
        start_time = time.time()
        Translate(input_path, output_path, target_language="en")
        elapsed_time = time.time() - start_time
        print(f"\nTotal time: {elapsed_time:.2f} seconds")