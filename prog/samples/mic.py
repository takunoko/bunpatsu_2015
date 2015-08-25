# coding: utf-8
import pyaudio
import wave

CHUNK = 1024
# CHUNK = 100
FORMAT = pyaudio.paInt16
CHANNELS = 1 # $BF~NO$N%A%c%s%M%k?t$K9g$o$;$FJQ99$9$kI,MW$,$"$k!#%$%d%[%sIUB0$O(B1
RATE = 44100

RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

# PC$B$K@\B3$5$l$F$$$k%*!<%G%#%*%G%P%$%9$N>pJs$rI=<((B
apiCnt = p.get_host_api_count()
print("Host API Count: %d" % apiCnt)
for cnt in range(apiCnt):
	print(p.get_host_api_info_by_index(cnt))

# $BF~NO%G%P%$%9$N;XDj(B
# $B$J$s$@$+(BWeb$B%+%a$O$&$^$/G'<1$7$F$J$$$_$?$$(B
input_deveice_index = 1

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

# $B2;@<%U%l!<%`$N%j%9%H(B
frames = []

# $B%k!<%W$N2s?t$@$17W;;$F7+$jJV$7$F$k(B
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	# $B%9%H%j!<%`$+$i(Bchunk$BJ,$N%G!<%?$,N/$^$C$?$i;}$C$F$/$k46$8(B?
 data = stream.read(CHUNK)
 frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

# $B=PNO7k2L$N=q$-9~$_(B
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# $B$3$NJU$G=q$-9~$`(Bwave$B$N@_Dj(B
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
# $B<B:]$N=q$-9~$_(B
wf.writeframes(b''.join(frames))
wf.close()
