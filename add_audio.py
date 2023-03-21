#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.

import sys,os,time
usage='''
    usage: %s [-f] path/to/video/files
        This program add audio to video or replace if it exists. If no audio files input then it add silent audio.
        -f      audio file
        --mix   mixing external audio source and audio from video
''' %(sys.argv[0])


def outvideoexists(outvideo):
    if os.path.exists(outvideo):
        if 'ans' not in globals():
            print 'Output file "%s" is exist. Replace this?[y/N]: ' %(outvideo),
            ans = sys.stdin.readline().strip()
        if ans=='' or ans=='N' or ans=='n':
            num=1
            while os.path.exists(outvideo.rsplit('.',1)[0]+'_%d.mp4' %(num)):
                num+=1
            outvideo=outvideo.rsplit('.',1)[0]+'_%d.mp4' %(num)
        elif ans=='y' or ans=='Y':
            print 'Overwriting file %s' %(outvideo)
        else:
            outvideo = ans

    outvideo = os.path.realpath(outvideo)
    return outvideo

if '--mix' in sys.argv:
    sys.argv.pop(sys.argv.index('--mix'))
    mix=True
else:
    mix=False

if '-f' in sys.argv:
    audio_file = sys.argv[sys.argv.index('-f')+1]
    sys.argv.pop(sys.argv.index('-f')+1)
    sys.argv.pop(sys.argv.index('-f'))

files = sys.argv[1:]

print 'Replace input file(s)? (N or additions for create a copy) [Y/n]: ',
ans = sys.stdin.readline().strip()

#audio_in = '-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100'
#audio_in = '-f alsa -i default'
audio_in = '-f pulse -i "alsa_output.usb-GeneralPlus_USB_Audio_Device-00.analog-stereo" '
#audio_in = '-f pulse -i "USB Audio Device"'
audio_out= '-c:a aac -shortest'
mixing_audio = '-filter_complex "[0:a][1:a]amerge=inputs=2[a]" -map 0:v -map "[a]" '


for i in files:
    i = os.path.realpath(i)
    outvideo_time=os.path.getmtime(i)
    if ans=='' or (ans in 'yYNn'):
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        num=1
        while os.path.exists(i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])):
            num+=1
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])
    else:
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+outvideo[1]

    cmd = 'ffmpeg -i %s ' %(i) # Video file is input
    if 'audio_file' in globals():
        cmd += "-stream_loop -1 -i %s " %(audio_file) # Audio file is input add
    else:
        cmd += audio_in + ' '  # Audio source is input add

    if mix:
        cmd += mixing_audio + ' '
    else:
        cmd += '-map 0:v -map 1:a '
    cmd += ' -c:v copy %s -y %s ' %(audio_out, outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-127)

    os.utime(outvideo, (outvideo_time,outvideo_time))

    if ans=='y' or ans=='Y' or ans=='':
        cmd = 'mv %s %s' %(outvideo,i) 
        print cmd
        os.system(cmd)
