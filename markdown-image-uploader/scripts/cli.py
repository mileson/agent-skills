#!/usr/bin/env python3
"""CLI tool for Markdown Image Uploader"""

import sys
from pathlib import Path

import click

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from uploader import MarkdownImageUploader


@click.command()
@click.argument('markdown_file', type=click.Path(exists=True))
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output file path (default: <input>_with_cdn.md)'
)
@click.option(
    '--article-name',
    type=str,
    help='Article name for path organization (default: extracted from H1 or filename)'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    default=None,
    help='Config file path (default: prefer config/my_hosts.yaml, fallback to config/image_hosts.yaml + secrets-vault)'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Simulate run without actual upload'
)
def main(markdown_file, output, article_name, config, dry_run):
    """
    Upload images in Markdown to image hosting service.

    Example:

        python cli.py article.md -o article_with_cdn.md

        python cli.py article.md --article-name "my-tutorial"
    """
    try:
        uploader = MarkdownImageUploader(config_path=config)

        if output is None:
            markdown_path = Path(markdown_file)
            output = markdown_path.parent / f"{markdown_path.stem}_with_cdn{markdown_path.suffix}"

        print(f"📄 Processing: {markdown_file}")
        print(f"📦 Output: {output}")
        print(f"🔐 Config source: {uploader.config_path}")
        print()

        if dry_run:
            print('⚠️  DRY RUN MODE - No actual upload will be performed')
            print()

        content, stats = uploader.process_markdown(
            markdown_file,
            output_path=output,
            article_name=article_name
        )

        if stats['uploaded'] > 0 or stats['skipped'] > 0:
            print('\n✅ Processing completed!')
            sys.exit(0)

        print('\n⚠️  No images were uploaded.')
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
