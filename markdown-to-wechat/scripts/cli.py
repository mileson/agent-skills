#!/usr/bin/env python3
"""
命令行工具：Markdown 转微信公众号格式
"""

import click
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

from scripts.converter import MarkdownToWeChatConverter


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出 HTML 文件路径（或图片路径，当使用 --to-image 时）')
@click.option('--theme', '-t', default='light-blue', help='主题名称（默认: light-blue）')
@click.option('--clipboard', '-c', is_flag=True, help='复制到剪贴板')
@click.option('--preview', '-p', is_flag=True, help='在浏览器中预览')
@click.option('--info', is_flag=True, help='显示主题信息')
@click.option('--to-image', '-i', is_flag=True, help='转换为 PNG 长图（需要安装 playwright）')
@click.option('--image-width', type=int, default=700, help='图片宽度（像素），默认 700')
@click.option('--zoom', type=float, default=2.0, help='图片缩放倍数（默认 2.0，适合移动端查看）')
@click.option('--top-padding', type=int, default=80, help='顶部留白（像素），默认 80，避免被设备刘海遮挡')
def convert_markdown(input_file, output, theme, clipboard, preview, info, to_image, image_width, zoom, top_padding):
    """
    将 Markdown 文件转换为微信公众号格式
    
    示例:
        python cli.py article.md -o output.html -c
        python cli.py article.md --theme light-blue --clipboard
        python cli.py article.md --info
        python cli.py article.md -o output.png --to-image
        python cli.py article.md --to-image --image-width 1200
    """
    try:
        # 创建转换器
        converter = MarkdownToWeChatConverter(theme_name=theme)
        
        # 显示主题信息
        if info:
            theme_info = converter.get_theme_info()
            click.echo('\n📋 主题信息:')
            click.echo(f"  名称: {theme_info['name']}")
            click.echo(f"  描述: {theme_info['description']}")
            click.echo(f"  版本: {theme_info['version']}")
            click.echo(f"  主色: {theme_info['primary_color']}\n")
        
        # 显示开始信息
        click.echo(f'\n📄 读取文件: {input_file}')
        click.echo(f'🎨 应用主题: {theme}')
        
        # 转换
        click.echo('⚙️  正在转换...')
        html_content = converter.convert_file(input_file, output)
        
        click.echo('✅ 转换完成!')
        
        # 保存文件
        if output:
            click.echo(f'💾 已保存到: {output}')
        
        # 复制到剪贴板
        if clipboard:
            if CLIPBOARD_AVAILABLE:
                try:
                    pyperclip.copy(html_content)
                    click.echo('📋 已复制到剪贴板，可直接粘贴到微信公众号后台!')
                except Exception as e:
                    click.echo(f'⚠️  复制到剪贴板失败: {e}', err=True)
            else:
                click.echo('⚠️  pyperclip 未安装，无法复制到剪贴板', err=True)
                click.echo('   提示: pip install pyperclip')
        
        # 浏览器预览
        if preview and not to_image:
            import webbrowser
            import tempfile
            
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
                f.write(html_content)
                temp_path = f.name
            
            webbrowser.open(f'file://{temp_path}')
            click.echo(f'🌐 已在浏览器中打开预览')
        
        # 转换为图片
        if to_image:
            import tempfile
            from pathlib import Path
            
            # 确定输出文件路径
            if output:
                # 如果用户指定了输出路径
                if output.endswith('.png'):
                    image_path = output
                    html_path = output.replace('.png', '.html')
                elif output.endswith('.html'):
                    html_path = output
                    image_path = output.replace('.html', '.png')
                else:
                    # 没有扩展名，添加 .png
                    image_path = output + '.png'
                    html_path = output + '.html'
            else:
                # 没有指定输出路径，使用输入文件名
                input_path = Path(input_file)
                image_path = str(input_path.with_suffix('.png'))
                html_path = str(input_path.with_suffix('.html'))
            
            # 保存 HTML 到临时文件或指定路径
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            click.echo(f'\n🖼️  正在转换为图片...')
            
            # 调用 html2image 模块
            try:
                from scripts.html2image import html_to_image
                
                success = html_to_image(
                    html_path=html_path,
                    output_path=image_path,
                    viewport_width=image_width,
                    full_page=True,
                    quality=100,
                    zoom_level=zoom,
                    top_padding=top_padding
                )
                
                if success:
                    click.echo(f'🎉 图片生成成功: {image_path}')
                    
                    # 如果需要预览，打开图片
                    if preview:
                        import webbrowser
                        webbrowser.open(f'file://{Path(image_path).absolute()}')
                        click.echo(f'🌐 已在浏览器中打开图片预览')
                else:
                    click.echo(f'❌ 图片生成失败', err=True)
                    
            except ImportError as e:
                click.echo(f'❌ 无法导入 html2image 模块: {e}', err=True)
                raise click.Abort()
            except Exception as e:
                click.echo(f'❌ 图片转换失败: {str(e)}', err=True)
                import traceback
                traceback.print_exc()
                raise click.Abort()
        
        click.echo('\n🎉 全部完成!\n')
        
    except FileNotFoundError as e:
        click.echo(f'❌ 文件错误: {str(e)}', err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f'❌ 转换失败: {str(e)}', err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


if __name__ == '__main__':
    convert_markdown()
