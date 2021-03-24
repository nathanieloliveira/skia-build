#! /usr/bin/env python3

import argparse, base64, os, platform, re, subprocess

system = {'Darwin': 'macos', 'Linux': 'linux', 'Windows': 'windows'}[platform.system()]
machine = {'AMD64': 'x64', 'x86_64': 'x64', 'arm64': 'arm64'}[platform.machine()]

def get_arg_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--debug', action='store_true')
  parser.add_argument('--version')
  parser.add_argument('--classifier')
  parser.add_argument('--android', action='store_true')
  parser.add_argument('--ndk-dir')
  parser.add_argument('--android-target-cpu', choices=['x86', 'x64', 'arm', 'arm64'])
  return parser

def is_android():
  args = get_arg_parser().parse_args()
  if args.android:
    return True
  return False

def ndk_dir():
  args = get_arg_parser().parse_args()
  return args.ndk_dir

def android_target_cpu():
  args = get_arg_parser().parse_args()
  return args.android_target_cpu

def version():
  args = get_arg_parser().parse_args()
  
  if args.version:
    return args.version

  branches = subprocess.check_output(['git', 'branch', '--contains', 'HEAD']).decode('utf-8')
  for match in re.finditer('chrome/(m\\d+)', branches):
    version = match.group(1)
  revision = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8')
  return version + '-' + revision.strip()[:10]

def build_type():
  (args, _) = get_arg_parser().parse_known_args()
  return 'Debug' if args.debug else 'Release'

def classifier():
  (args, _) = get_arg_parser().parse_known_args()
  return '-' + args.classifier if args.classifier else ''
  
def github_headers():
  if os.environ.get('GITHUB_BASIC'):
    auth = 'Basic ' + base64.b64encode(os.environ.get('GITHUB_BASIC').encode('utf-8')).decode('utf-8')
  else:
    auth = 'token ' + os.environ.get('GITHUB_TOKEN')
  return {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': auth
  }

def archive_name():
  if is_android():
    target_cpu = android_target_cpu()
    if target_cpu is None:
      return None
    target = 'Skia-' + version() + '-android-' + build_type() + '-' + target_cpu + classifier() + '.zip'
  else:
    target = 'Skia-' + version() + '-' + system + '-' + build_type() + '-' + machine + classifier() + '.zip'
  return target