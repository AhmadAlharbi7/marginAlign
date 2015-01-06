from jobTree.scriptTree.target import Target
from margin.utils import chainSamFile, realignSamFileTargetFn
import os
from sonLib.bioio import system
from margin.utils import AlignedPair, getFastaDictionary, getFastqDictionary, getExonerateCigarFormatString, samIterator

class AbstractMapper(Target):
    """Base class for mappers. Inherit this class to create a mapper
    """
    def __init__(self, readFastqFile, referenceFastaFile, outputSamFile, inputHmmFile, outputHmmFile):
        Target.__init__(self)
        self.readFastqFile = readFastqFile
        self.referenceFastaFile = referenceFastaFile
        self.outputSamFile = outputSamFile
        self.inputHmmFile=inputHmmFile
        self.outputHmmFile=outputHmmFile
        
    def chainSamFile(self):
        """Converts the sam file so that there is at most one global alignment of each read
        """ 
        tempSamFile = os.path.join(self.getLocalTempDir(), "temp.sam")
        system("cp %s %s" % (self.outputSamFile, tempSamFile))
        chainSamFile(tempSamFile, self.outputSamFile, self.readFastqFile, self.referenceFastaFile)
    
    def realignSamFile(self, gapGamma=0.5, matchGamma=0.0, doEm=False,  useTrainedModel=False, trainedModelFile="blasr_hmm_0.txt"):
        """Chains and then realigns the resulting global alignments.
        """
        tempSamFile = os.path.join(self.getGlobalTempDir(), "temp.sam")
        if useTrainedModel and doEm:
            raise RuntimeError("Attempting to train stock model")
        system("cp %s %s" % (self.outputSamFile, tempSamFile))
        if doEm:
            hmmFile = self.outputHmmFile
        else:
            hmmFile = self.inputHmmFile
        self.addChildTargetFn(realignSamFileTargetFn, args=(tempSamFile, self.outputSamFile, 
                                                            self.readFastqFile, self.referenceFastaFile, gapGamma, matchGamma, hmmFile, doEm))
