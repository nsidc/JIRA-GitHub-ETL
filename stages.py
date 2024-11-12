import csv
import re
import os
        
#
# Generic abstract stage class
# 
class Stage:

    def execute(self, group):
        raise NotImplementedError("Called abstract")
    
    def on_terminate(self):
        pass

#
# Output port implementation which passes data to the next stage 
#
class OutputPort:
    receiver: Stage = None

    def send(self, value):
        if self.receiver != None:
            self.receiver.execute(value)
        else:
            print("Missing receiver")

    def on_terminate(self):
        if (self.receiver != None):
            self.receiver.on_terminate()
        
#
# Generic Consumer Stage
#
class ConsumerStage:

    output_port: OutputPort
    
    def __init__(self):
        self.output_port = OutputPort()

    def execute(self, group):
        raise NotImplementedError("Called abstract")
    
    def on_terminate(self):
        self.output_port.on_terminate()

#
# Generic Producer Stage
#
class ProducerStage:

    output_port: OutputPort
    
    def __init__(self):
        self.output_port = OutputPort()
    
    def execute(self):
        raise NotImplementedError("Called abstract")
    
    def on_terminate(self):
        self.output_port.on_terminate()

#
# Generic Sink Stage
#
class SinkStage:

    def execute(self, group):
        raise NotImplementedError("Called abstract")
    
    def on_terminate(self):
        pass

# end
