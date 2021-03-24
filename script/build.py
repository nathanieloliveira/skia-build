#! /usr/bin/env python3

import common, os, subprocess, sys

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'skia'))

  build_type = common.build_type()
  is_android = common.is_android()

  if build_type == 'Debug':
    args = ['is_debug=true']
  else:
    args = ['is_official_build=true']

  if is_android:
    print("this is android")
    android_target_cpu = common.android_target_cpu()
    if android_target_cpu is None:
      print("need to set --android-target-cpu")
      return -1
    args += ['target_cpu="' + android_target_cpu + '"']
  else:
    args += ['target_cpu="' + common.machine + '"']

  args += [
    'skia_use_system_expat=false',
    'skia_use_system_libjpeg_turbo=false',
    'skia_use_system_libpng=false',
    'skia_use_system_libwebp=false',
    'skia_use_system_zlib=false',
    'skia_use_sfntly=false',
    'skia_use_freetype=true',
    'skia_use_system_freetype2=false',
    # 'skia_use_harfbuzz=true',
    'skia_use_system_harfbuzz=false',
    'skia_pdf_subset_harfbuzz=true',
    # 'skia_use_icu=true',
    'skia_use_system_icu=false',
    # 'skia_enable_skshaper=true',
    # 'skia_enable_svg=true',
    'skia_enable_skottie=true'
  ]

  if is_android:
    args += [
      'ndk="' + common.ndk_dir() + '"',
    ]
  elif 'macos' == common.system:
    args += [
      # 'skia_enable_gpu=true',
      # 'skia_use_gl=true',
      'skia_use_metal=true',
      'extra_cflags_cc=["-frtti"]'
    ]
    if 'arm64' == common.machine:
      args += ['extra_cflags=["-stdlib=libc++"]']
    else:
      args += ['extra_cflags=["-stdlib=libc++", "-mmacosx-version-min=10.13"]']
  elif 'linux' == common.system:
    args += [
      # 'skia_enable_gpu=true',
      # 'skia_use_gl=true',
      'extra_cflags_cc=["-frtti"]',
      'cxx="g++-9"',
    ]
  elif 'windows' == common.system:
    args += [
      # 'skia_use_angle=true',
      'skia_use_direct3d=true',
      'extra_cflags=["-DSK_FONT_HOST_USE_SYSTEM_SETTINGS"]',
    ]

  if is_android:
    out = os.path.join('out', build_type + '-android-' + android_target_cpu)
  else:
    out = os.path.join('out', build_type + '-' + common.machine)
  gn = 'gn.exe' if 'windows' == common.system else 'gn'
  subprocess.check_call([os.path.join('bin', gn), 'gen', out, '--args=' + ' '.join(args)])
  ninja = 'ninja.exe' if 'windows' == common.system else 'ninja'
  subprocess.check_call([os.path.join('..', 'depot_tools', ninja), '-C', out, 'skia', 'modules'])

  return 0

if __name__ == '__main__':
  sys.exit(main())
