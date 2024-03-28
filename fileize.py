import argparse
import io
import sys
import zipfile

import requests

from repotools.utils import Utils


class Fileize:
    def __init__(self, lang: str):
        self.lang = lang
        self.utils = Utils(lang)

    def download_repo(self, repo_url, output_file, lang, keep_comments=False, branch_or_tag="master"):
        """Download and process files from a GitHub repository."""
        download_url = f"{repo_url}/archive/refs/heads/{branch_or_tag}.zip"

        print(download_url)
        response = requests.get(download_url)

        if response.status_code == 200:
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            with open(output_file, "w", encoding="utf-8") as outfile:
                for file_path in zip_file.namelist():
                    # Skip directories, non-language files, less likely useful files, hidden directories, and test files
                    if file_path.endswith("/") or not self.utils.is_file_type(
                            file_path) or not self.utils.is_likely_useful_file(file_path):
                        continue
                    file_content = zip_file.read(file_path).decode("utf-8")

                    # Skip test files based on content and files with insufficient substantive content
                    if self.utils.is_test_file(file_content, lang) or not self.utils.has_sufficient_content(
                            file_content):
                        continue
                    if lang == "python" and not keep_comments:
                        try:
                            file_content = self.utils.remove_comments_and_docstrings(file_content)
                        except SyntaxError:
                            # Skip files with syntax errors
                            continue
                    outfile.write(f"// File: {file_path}\n" if lang == "go" else f"# File: {file_path}\n")
                    outfile.write(file_content)
                    outfile.write("\n\n")
        else:
            print(f"Failed to download the repository. Status code: {response.status_code}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Download and process files from a GitHub repository.')
    parser.add_argument('repo_url', type=str, help='The URL of the GitHub repository')
    parser.add_argument('--lang', type=str, choices=['go', 'python'], default='python',
                        help='The programming language of the repository')
    parser.add_argument('--keep-comments', action='store_true',
                        help='Keep comments and docstrings in the source code (only applicable for Python)')
    parser.add_argument('--branch_or_tag', type=str, help='The branch or tag of the repository to download',
                        default="master")

    args = parser.parse_args()

    fileize = Fileize(lang=args.lang)

    output_file = f"{args.repo_url.split('/')[-1]}_{args.lang}.txt"

    fileize.download_repo(args.repo_url, output_file, args.lang, args.keep_comments, args.branch_or_tag)


if __name__ == '__main__':
    main()
