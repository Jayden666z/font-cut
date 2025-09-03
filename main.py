#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTF 字体裁剪工具
直接在脚本中指定要保留的文字
"""

import os
import sys
from pathlib import Path

try:
    from fontTools.subset import Subsetter
    from fontTools.ttLib import TTFont
except ImportError:
    print("错误: 请先安装 fonttools")
    print("运行: pip install fonttools")
    sys.exit(1)

# ==================== 配置区域 ====================
# 在这里直接修改你要保留的文字
KEEP_TEXT = """滴天髓"""

# 输入和输出文件路径配置
INPUT_FONT = "jhlst.ttf"  # 修改为你的输入字体文件路径
OUTPUT_FONT = "jhlst_sub.ttf"  # 修改为你想要的输出文件路径

# 其他选项
KEEP_BASIC_LATIN = False  # 是否保留基本拉丁字符（空格、标点等）
KEEP_NUMBERS = False  # 是否保留数字
KEEP_PUNCTUATION = False  # 是否保留常用标点符号


# ==================== 配置区域结束 ====================


class FontSubsetter:
    def __init__(self):
        self.supported_formats = ['.ttf', '.otf', '.woff', '.woff2']

    def validate_font_file(self, font_path):
        """验证字体文件是否有效"""
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字体文件不存在: {font_path}")

        file_ext = Path(font_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的字体格式: {file_ext}")

        try:
            font = TTFont(font_path)
            font.close()
            return True
        except Exception as e:
            raise ValueError(f"无效的字体文件: {e}")

    def get_font_info(self, font_path):
        """获取字体基本信息"""
        try:
            font = TTFont(font_path)

            # 获取字体名称
            name_table = font['name']
            font_name = "Unknown"
            for record in name_table.names:
                if record.nameID == 1:  # Font Family name
                    font_name = record.toUnicode()
                    break

            # 获取字符数量
            cmap = font.getBestCmap()
            char_count = len(cmap) if cmap else 0

            # 获取文件大小
            file_size = os.path.getsize(font_path)

            font.close()

            return {
                'name': font_name,
                'char_count': char_count,
                'file_size': file_size
            }
        except Exception as e:
            return {'name': 'Unknown', 'char_count': 0, 'file_size': 0}

    def prepare_text(self, text, keep_basic_latin=True, keep_numbers=True, keep_punctuation=True):
        """准备要保留的文字"""
        # 去除重复字符
        unique_chars = set(text)

        # 添加基本字符
        if keep_basic_latin:
            # 基本拉丁字符：空格、基本标点
            unique_chars.update(' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

        if keep_numbers:
            unique_chars.update('0123456789')

        if keep_punctuation:
            # 常用中文标点
            unique_chars.update('。，、；：？！""''【】《》（）·—…')

        return ''.join(sorted(unique_chars))

    def subset_font(self, input_path, output_path, text):
        """裁剪字体文件"""

        # 验证输入文件
        self.validate_font_file(input_path)

        try:
            # 使用 Subsetter 类进行字体裁剪
            font = TTFont(input_path)
            
            # 创建 Subsetter 实例
            subsetter = Subsetter()
            
            # 设置要保留的字符
            subsetter.populate(text=text)
            
            # 应用裁剪
            subsetter.subset(font)
            
            # 保存裁剪后的字体
            font.save(output_path)
            font.close()
            
            return True
        except Exception as e:
            raise RuntimeError(f"字体裁剪失败: {e}")

    def format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    subsetter = FontSubsetter()

    try:
        print("🔤 TTF 字体裁剪工具")
        print("=" * 50)

        # 检查输入文件
        if not os.path.exists(INPUT_FONT):
            print(f"❌ 输入字体文件不存在: {INPUT_FONT}")
            print("请修改脚本中的 INPUT_FONT 变量为正确的文件路径")
            return

        # 准备要保留的文字
        final_text = subsetter.prepare_text(
            KEEP_TEXT,
            KEEP_BASIC_LATIN,
            KEEP_NUMBERS,
            KEEP_PUNCTUATION
        )

        print(f"📁 输入文件: {INPUT_FONT}")
        print(f"📁 输出文件: {OUTPUT_FONT}")
        print(f"📝 要保留的字符数: {len(final_text)}")
        print(f"📝 字符预览: {final_text[:50]}{'...' if len(final_text) > 50 else ''}")
        print()

        # 获取原始字体信息
        original_info = subsetter.get_font_info(INPUT_FONT)
        print(f"原始字体信息:")
        print(f"  名称: {original_info['name']}")
        print(f"  大小: {subsetter.format_file_size(original_info['file_size'])}")
        print(f"  字符数: {original_info['char_count']}")
        print()

        # 执行裁剪
        print("⏳ 正在裁剪字体...")
        subsetter.subset_font(INPUT_FONT, OUTPUT_FONT, final_text)

        # 显示结果
        if os.path.exists(OUTPUT_FONT):
            subset_info = subsetter.get_font_info(OUTPUT_FONT)
            print("✅ 字体裁剪完成!")
            print()
            print(f"裁剪后字体信息:")
            print(f"  文件: {OUTPUT_FONT}")
            print(f"  大小: {subsetter.format_file_size(subset_info['file_size'])}")
            print(f"  字符数: {subset_info['char_count']}")

            # 计算压缩比
            if original_info['file_size'] > 0:
                compression_ratio = (1 - subset_info['file_size'] / original_info['file_size']) * 100
                print(f"  大小减少: {compression_ratio:.1f}%")

            print()
            print("🎉 任务完成! 你可以在以下位置找到裁剪后的字体:")
            print(f"   {os.path.abspath(OUTPUT_FONT)}")
        else:
            print("❌ 字体裁剪失败")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 显示要保留的文字内容
    print("当前配置的保留文字:")
    print("-" * 30)
    print(KEEP_TEXT.strip())
    print("-" * 30)
    print()

    # 询问是否继续
    try:
        response = input("是否使用以上配置进行字体裁剪? (y/n): ").lower().strip()
        if response in ['y', 'yes', '是', '']:
            main()
        else:
            print("已取消操作。请修改脚本中的 KEEP_TEXT 变量后重新运行。")
    except KeyboardInterrupt:
        print("\n已取消操作。")
