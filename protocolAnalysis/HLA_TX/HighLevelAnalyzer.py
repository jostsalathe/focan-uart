# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame

class TxMsg:
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

    def getDriveMode(self) -> int:
        '''
        byte 3, bits 0...1
        0: pedal drive, 1: electric drive, 2: both (set with P10)
        '''
        return int.from_bytes(self.msgBytes[3:4], 'big') & 0x3

    def getGear(self) -> int:
        '''
        byte 4, bits 0...1 (mirrored in bits 2...3 for unknown reason)
        0: off, 1: eco, 2: mid, 3: high
        '''
        return int.from_bytes(self.msgBytes[4:5], 'big') & 0x3

    def getKickStart(self) -> int:
        '''
        byte 5, bit 6
        if bit is 1 the motor will only start if the wheel is already turning (set with P09)
        '''
        return (int.from_bytes(self.msgBytes[5:6], 'big') >> 6) & 0x1

    def getLightEnable(self) -> int:
        '''
        byte 5, bit 5
        bit is 1 if the light is turned on
        '''
        return (int.from_bytes(self.msgBytes[5:6], 'big') >> 5) & 0x1

    def getNSpeedMagnets(self) -> int:
        '''
        byte 6
        number of speed magnets ranging from 0 to 255 (set with P07)
        '''
        return int.from_bytes(self.msgBytes[6:7], 'big')

    def getWheelDiameter(self) -> int:
        '''
        byte 7, bit 0 and byte 8
        wheel diameter in 1/10 inch ranging from 2.5 to 50.0 (set with P06)
        '''
        return int.from_bytes(self.msgBytes[7:9], 'big') & 0x1FF

    def getBoostSensitivity(self) -> int:
        '''
        byte 9, bits 0...4
        boost sensitivity ranging from 1 to 24 (set with P11)
        '''
        return int.from_bytes(self.msgBytes[9:10], 'big') & 0x1F

    def getBoostStrength(self) -> int:
        '''
        byte 10, bits 0...2
        boost start strength ranging from 0 to 5 (set with P12)
        '''
        return int.from_bytes(self.msgBytes[10:11], 'big') & 0x7

    def getSpeedLimit(self) -> int:
        '''
        byte 12
        speed limit in km/h ranging from 0 to 100 (set with P08)
        '''
        return int.from_bytes(self.msgBytes[12:13], 'big')

    def getCurrentLimit(self) -> int:
        '''
        byte 13
        current limit in A ranging from 1 to 20 (set with P14)
        '''
        return int.from_bytes(self.msgBytes[13:14], 'big') & 0x1F

    def getUnderVoltage(self) -> float:
        '''
        bytes 14...15
        Undervoltage threshold in 1/10 volt (combination of P03 (range: 24V/36V/48V) and P15 (decivolt adjustment)
        '''
        return int.from_bytes(self.msgBytes[14:16], 'big')*0.1

    def getSpeed(self) -> int:
        '''
        bytes 16...17
        speed lever position 0...1000
        '''
        return int.from_bytes(self.msgBytes[16:18], 'big')

    def getCruiseEnable(self) -> int:
        '''
        byte 18, bits 6
        cruise enable (set with P17)
        '''
        return (int.from_bytes(self.msgBytes[18:19], 'big') >> 6) & 0x1

    def getPowerMagnetType(self) -> int:
        '''
        byte 18, bits 0...3
        power magnetic steel disc type 5/8/12 (set with P13)
        '''
        return int.from_bytes(self.msgBytes[18:19], 'big') & 0xF

    def getCRC(self) -> int:
        '''
        byte 19
        reveng.exe: width=8  poly=0x01  init=0x00  refin=false  refout=false  xorout=0x00  check=0x31  residue=0x00  name=(none)
        see https://reveng.sourceforge.io/readme.htm
        '''
        return int.from_bytes(self.msgBytes[19:20], 'big')

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
        'GZ3_TX': {
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
                if len(self.frames) == 20:
                    'The new frame came more than 50 ms after the last frame. Time to analyze!'
                    msg = TxMsg(self.frames)
                    
                    if self.lastMsgBytes != msg.msgBytes:
                        print(str(self.msgCounter).rjust(4), msg)
                        # print(msg)
                        self.lastMsgBytes = msg.msgBytes
                    
                    data = {
                        't': float(self.frames[0].start_time - self.tBegin),
                        'driveMode': str(msg.getDriveMode()),
                        'gear': str(msg.getGear()),
                        'kickStart': str(msg.getKickStart()),
                        'lightEnable': str(msg.getLightEnable()),
                        'nSpeedMagnets': str(msg.getNSpeedMagnets()),
                        'wheelDiameter': str(msg.getWheelDiameter()),
                        'boostSensitivity': str(msg.getBoostSensitivity()),
                        'boostStrength': str(msg.getBoostStrength()),
                        'speedLimit': str(msg.getSpeedLimit()),
                        'currentLimit': str(msg.getCurrentLimit()),
                        'underVoltage': str(msg.getUnderVoltage()),
                        'speed': str(msg.getSpeed()),
                        'cruiseEnable': str(msg.getCruiseEnable()),
                        'powerMagnetType': str(msg.getPowerMagnetType()),
                        'CRC': str(msg.getCRC())
                    }
                    
                    result = AnalyzerFrame('GZ3_TX', self.frames[0].start_time, self.frames[-1].end_time, data)
                    self.msgCounter += 1

                self.frames = [frame]

            else:
                self.frames.append(frame)

        return result
