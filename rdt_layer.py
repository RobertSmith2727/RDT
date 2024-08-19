from segment import Segment


class RDTLayer(object):

    #######################################################################
    # The length of the string data that will be sent per packet...
    DATA_LENGTH = 4
    # Receive window size for flow-control
    FLOW_CONTROL_WIN_SIZE = 10  # 15 # in characters
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0

    #######################################################################

    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        self.lastAckReceived = 0
        self.lastSeqSent = 0
        self.lastSeqAdded = 0
        self.dataReceived = ""
        self.ackowledgement = -1

    ###################################################################

    def setSendChannel(self, channel):
        self.sendChannel = channel

    ###################################################################

    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    ##################################################################

    def setDataToSend(self, data):
        self.dataToSend = data

    # ####################################################################

    def getDataReceived(self):
        """returns data received from sender"""

    #######################################################################

        print('Data Received:')
        return self.dataReceived

    #######################################################################

    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    #######################################################################

    def processSend(self):
        """processes data and sends data up to window size"""

        # Set window and slices for send data
        window = RDTLayer.FLOW_CONTROL_WIN_SIZE
        startSlice = self.lastAckReceived * RDTLayer.DATA_LENGTH
        endSlice = startSlice + RDTLayer.DATA_LENGTH
        seqnum = self.lastAckReceived
        for x in range(window):
            segmentSend = Segment()
            seqnum += 1
            data = self.dataToSend[startSlice:endSlice]
            if data != '':
                startSlice += RDTLayer.DATA_LENGTH
                endSlice += RDTLayer.DATA_LENGTH
                # Display sending segment
                segmentSend.setData(seqnum, data)
                print("Sending segment: ", segmentSend.to_string())
                # Unreliable sendChannel to send the segment
                self.sendChannel.send(segmentSend)

    #######################################################################

    def processReceiveAndSendRespond(self):
        segmentAck = Segment()

        # returns incoming segments
        listIncomingSegments = self.receiveChannel.receive()

        for segment in listIncomingSegments:
            receivedSegment = segment.to_string()
            print(receivedSegment)
            sequence = segment.seqnum
            data = segment.payload

            if not segment.checkChecksum():
                continue

            # add data, update lastSeqAdded, and ack
            if sequence == self.lastSeqAdded + 1:
                self.dataReceived += data
                self.lastSeqAdded += 1
                self.ackowledgement = sequence

            # get ack received
            if sequence == -1:
                self.lastAckReceived = segment.acknum

        # cumulative ack (GNB)
        acknum = self.ackowledgement

        # Display response segment
        segmentAck.setAck(acknum)
        print("Sending ack: ", segmentAck.to_string())

        # Use the unreliable sendChannel to send the ack packet
        self.sendChannel.send(segmentAck)
