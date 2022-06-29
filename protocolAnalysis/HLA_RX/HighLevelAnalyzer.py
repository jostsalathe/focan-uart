# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame

class RxMsg:
    def __init__(self, frames: list):
        self.msgBytes = bytes()
        for fr in frames:
            self.msgBytes += fr.data['data']

    def getProbablyDeviceAddress(self) -> int:
        '''
        byte 0
        1: from display, 2: to display
        '''
        return int.from_bytes(self.msgBytes[0:1], 'big')

    def getProbablyPacketLength(self) -> int:
        '''
        byte 1
        including all bytes. 20 from display, 14 to display
        '''
        return int.from_bytes(self.msgBytes[1:2], 'big')

    def getProbablySoftwareRevision(self) -> int:
        '''
        byte 2
        1 from both my devices
        '''
        return int.from_bytes(self.msgBytes[2:3], 'big')

    def getMsPerRev(self) -> int:
        '''
        bytes 8...9
        wheel speed in milliseconds/revolution ranging from 0 to 31456
        '''
        return int.from_bytes(self.msgBytes[8:10], 'big')

    def getSpeed(self) -> float:
        '''
        assuming wheel diameter of D=9.5", perimeter P=758mm
        and using time per revolution t=getMsPerRev in ms
        velocity then is v = 3.6 * P / t
        '''
        result = 3.6*758/self.getMsPerRev()
        return result if result > 0.1 else 0

    def getCRC(self) -> int:
        '''
        byte 13
        reveng.exe: width=8  poly=0x01  init=0x00  refin=false  refout=false  xorout=0x00  check=0x31  residue=0x00  name=(none)
        see https://reveng.sourceforge.io/readme.htm
        '''
        return int.from_bytes(self.msgBytes[13:14], 'big')

    def getBitString(self, begin=0, n=0) -> str:
        if n == 0:
            end = len(self.msgBytes)
        else:
            end = begin + n
        result = ''
        for i in range(len(self.msgBytes)):
            if i < begin:
                pass
            elif i < end:
                result += '{0:b}'.format(int.from_bytes(self.msgBytes[i:i+1], 'big')).rjust(8, '0') + ' '
            else:
                break
        return result[:-1]#.replace('0', '---').replace('1', ' | ')

    def __str__(self) -> str:
        result = ''
        for i in range(int(len(self.msgBytes)/2)):
            result += self.msgBytes[i*2:(i+1)*2].hex() + ' '
        return result[:-1]

# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'GZ3_RX': {
            'format': '{{data.speed}} '
        }
    }

    def __init__(self):
        '''
        Initialize HLA.
        '''
        self.frames = []
        self.lastMsgBytes = bytes()
        self.msgCounter = 0
        self.tBegin = None

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''
        result = None

        if frame.type == 'data':
            if self.tBegin == None:
                self.tBegin = frame.start_time
            if len(self.frames) != 0 and float(frame.start_time - self.frames[-1].start_time) > 0.05:
                if len(self.frames) == 14:
                    'The new frame came more than 50 ms after the last frame. Time to analyze!'
                    msg = RxMsg(self.frames)
                    
                    if self.lastMsgBytes != msg.msgBytes:
                        print(str(self.msgCounter).rjust(4), msg)
                        # print(str(self.msgCounter).rjust(4), msg.getBitString(8, 2))
                        self.lastMsgBytes = msg.msgBytes
                    
                    data = {
                        't': float(self.frames[0].start_time - self.tBegin),
                        'speed': str(msg.getSpeed()),
                        'CRC': str(msg.getCRC())
                    }
                    
                    result = AnalyzerFrame('GZ3_RX', self.frames[0].start_time, self.frames[-1].end_time, data)
                    self.msgCounter += 1

                self.frames = [frame]

            else:
                self.frames.append(frame)

        return result
