#! /usr/bin/env python3

import argparse, common, os, pathlib, platform, re, subprocess, sys

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir))
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--version', required=True)
  args = parser.parse_args()

  # Clone depot_tools
  if not os.path.exists("depot_tools"):
    subprocess.check_call(["git", "clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git", "depot_tools"])

  # Clone Skia
  match = re.match('(m\\d+)(?:-([0-9a-f]+))?', args.version)
  if not match:
    raise Exception('Expected --version "m<ver>-<sha>", got "' + args.version + '"')
  branch = "chrome/" + match.group(1)
  commit = match.group(2)

  if os.path.exists("skia"):
    os.chdir("skia")
    if subprocess.check_output(["git", "branch", "--list", branch]):
      print("> Advancing", branch)
      subprocess.check_call(["git", "checkout", "-B", branch])
      subprocess.check_call(["git", "fetch"])
      subprocess.check_call(["git", "reset", "--hard", "origin/" + branch])
    else:
      print("> Fetching", branch)
      subprocess.check_call(["git", "fetch", "origin", branch + ":remotes/origin/" + branch])
      subprocess.check_call(["git", "checkout", branch])
  else:
    print("> Cloning", branch)
    subprocess.check_call(["git", "clone", "https://skia.googlesource.com/skia", "--quiet", "--branch", branch, "skia"])
    os.chdir("skia")

  # Checkout commit
  print("> Checking out", commit)
  subprocess.check_call(["git", "-c", "advice.detachedHead=false", "checkout", commit])

  # Apply patches
  subprocess.check_call(["git", "reset", "--hard"])
  for x in pathlib.Path(os.pardir, 'patches').glob('*.patch'):
    print("> Applying git patch", x)
    subprocess.check_call(["git", "apply", str(x)])

  # git deps
  if 'windows' == common.system:
    env = os.environ.copy()
    env['PYTHONHTTPSVERIFY']='0'
    subprocess.check_call(["python", "tools/git-sync-deps"], env=env)
  else:
    subprocess.check_call(["python2", "tools/git-sync-deps"])

  # Apply third_party patches
  externals = pathlib.Path("third_party/externals").resolve()
  for x in pathlib.Path(os.pardir, 'patches/external').resolve().glob('*.patch'):
    print("> Applying third party patch", x)
    lib = pathlib.Path(externals, str(x.stem))
    os.chdir(lib)
    subprocess.check_call(["git", "reset", "--hard"])
    subprocess.check_call(["git", "apply", str(x)])

  return 0

if __name__ == '__main__':
  sys.exit(main())
