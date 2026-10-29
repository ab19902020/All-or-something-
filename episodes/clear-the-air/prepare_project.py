#!/usr/bin/env python3
"""Install this source package into the existing AnimnationStuido- working checkout.

python prepare_project.py /path/to/animation-studio
Copy final voiceovers back to this source directory before committing them.
"""
import argparse,pathlib,shutil,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent

def copy(src,dst):
    shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','build','.env'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('studio',type=pathlib.Path);a=ap.parse_args()
    root=a.studio.resolve()
    if not (root/'studio/film/__main__.py').is_file():raise SystemExit('Not an existing Animation Studio checkout')
    # The historical episode's exact engine patch supports lip_lt and the whole-image poses.
    patch=HERE/'pack/studio-engine.patch'
    reverse=subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=root,capture_output=True)
    if reverse.returncode:
        check=subprocess.run(['git','apply','--check',str(patch)],cwd=root,capture_output=True,text=True)
        if check.returncode:raise SystemExit('Engine differs from the pinned historical base; review the patch before installing.')
        subprocess.run(['git','apply',str(patch)],cwd=root,check=True)
    copy(HERE/'library-overlay',root/'library')
    ep=root/'episodes/clear-the-air'
    for name in ['film','voices','voiceovers','pack']:
        if (HERE/name).exists():copy(HERE/name,ep/name)
    for name in ['script.md','generate_voices.py']:
        shutil.copy2(HERE/name,ep/name)
    print('Prepared',ep)
    print('Next: generate_voices.py; python -m studio.film clear-the-air lines; timeline; still; sound; render; sheet; lips; check')

if __name__=='__main__':main()
