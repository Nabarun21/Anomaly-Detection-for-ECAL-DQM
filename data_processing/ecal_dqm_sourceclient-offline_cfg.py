# HARDCODED OPTIONS

import os, sys

#Relevant for P5-style and normal input source
hardcoded_workflow = "/All/Run2017/CentralDAQ"
hardcoded_prescaleFactor = 1
hardcoded_verbosity = 1
hardcoded_maxEvents = -1
hardcoded_readRaw = False
hardcoded_runNumber = 0
hardcoded_inputPath = "inputFileList.txt"

#Relevant for normal input source only
hardcoded_lumisToProcess = []
# hardcoded_eventToProcess = 0

# Run sanity checks
# if (hardcoded_eventToProcess > 0 and hardcoded_lumisToProcess == 0): sys.exit("Enter lumi block number for given event!")
# if (hardcoded_eventToProcess > 0 and hardcoded_maxEvents != 1): sys.exit("MaxEvents should be set to 1")
if (hardcoded_readRaw):
  if (hardcoded_runNumber == 0 or hardcoded_inputPath == ""):
    sys.exit("runNumber and inputPath must both be set")
else:
  if (len(hardcoded_lumisToProcess) > 0 and hardcoded_runNumber == 0):
    sys.exit("if lumis to process is a finite list, runNumber must not be 0")

import FWCore.ParameterSet.Config as cms

process = cms.Process("offlineECALDQM")

### Load cfis ###

if (hardcoded_readRaw):
  process.load("DQM.Integration.config.inputsource_cfi")
# else:
#   process.load("DQM.Integration.config.fileinputsource_cfi")

# Will probably not work until DQM.Integration.config.fileinputsource_cfi is modified to not include its own VarParsing
# options = VarParsing.VarParsing()
# options.register("inputPath", default="", mult=VarParsing.VarParsing.multiplicity.singleton, mytype=VarParsing.VarParsing.varType.string, info="input file")
# options.register("workflow", default="/All/Run2017/CentralDAQ", mult=VarParsing.VarParsing.multiplicity.singleton, mytype=VarParsing.VarParsing.varType.string, info="offline workflow")
# options.register("prescaleFactor", default=10, mult=VarParsing.VarParsing.multiplicity.singleton, mytype=VarParsing.VarParsing.varType.int, info="prescale factor")
# options.register("maxEvents", default=10, mult=VarParsing.VarParsing.multiplicity.singleton, mytype=VarParsing.VarParsing.varType.int, info="max number of events to analyze")
# options.register("readRaw", default=False, mult=VarParsing.VarParsing.multiplicity.singleton, mytype=VarParsing.VarParsing.varType.bool, info="True for RAW input, 1 for edm-formatted ROOT input")
# options.register("verbosity", default=1, mult=VarParsing.VarParsing.multiplicity.singleton, mytype=VarParsing.VarParsing.varType.int, info="Verbosity")
# options.parseArguments()

process.load("DQM.Integration.config.environment_cfi")

process.load("DQM.Integration.config.FrontierCondition_GT_cfi")

# process.load("DQM.Integration.config.FrontierCondition_GT_autoExpress_cfi")
#process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
#process.load("CalibCalorimetry.EcalLaserCorrection.ecalLaserCorrectionService_cfi")

process.load("FWCore.Modules.preScaler_cfi")

process.load("Configuration.StandardSequences.GeometryRecoDB_cff")

#process.load("Geometry.CaloEventSetup.CaloGeometry_cfi")
#process.load("Geometry.CaloEventSetup.CaloTopology_cfi")
#process.load("Geometry.CaloEventSetup.EcalTrigTowerConstituents_cfi")
#process.load("Geometry.CMSCommonData.cmsIdealGeometryXML_cfi")
#process.load("Geometry.EcalMapping.EcalMapping_cfi")
#process.load("Geometry.EcalMapping.EcalMappingRecord_cfi")

process.load("Configuration.StandardSequences.RawToDigi_Data_cff")

#process.load("L1Trigger.Configuration.L1RawToDigi_cff")
#process.load("SimCalorimetry.EcalTrigPrimProducers.ecalTriggerPrimitiveDigis_cfi")

process.load("Configuration.StandardSequences.Reconstruction_cff")

#process.load("RecoLuminosity.LumiProducer.bunchSpacingProducer_cfi")

# COMMENT FOLLOWING THREE?

process.load("RecoLocalCalo.EcalRecProducers.ecalMultiFitUncalibRecHit_cfi")
# process.load("RecoLocalCalo.EcalRecProducers.ecalWeightUncalibRecHit_cfi")

process.load("RecoLocalCalo.EcalRecProducers.ecalDetIdToBeRecovered_cfi")

process.load("RecoLocalCalo.EcalRecProducers.ecalRecHit_cfi")
# process.load("RecoLocalCalo.EcalRecProducers.ecalPreshowerRecHit_cfi")

# process.load('RecoParticleFlow.PFClusterProducer.particleFlowRecHitPS_cfi')
# process.load('RecoParticleFlow.PFClusterProducer.particleFlowClusterPS_cfi')
# process.load('RecoParticleFlow.PFClusterProducer.particleFlowRecHitECAL_cfi')
# process.load('RecoParticleFlow.PFClusterProducer.particleFlowClusterECALUncorrected_cfi')
# process.load('RecoParticleFlow.PFClusterProducer.particleFlowClusterECAL_cfi')
# process.load('RecoEcal.EgammaClusterProducers.particleFlowSuperClusterECAL_cfi')
# process.load('RecoEcal.EgammaClusterProducers.particleFlowSuperClusteringSequence_cff')
# process.load('RecoVertex.BeamSpotProducer.BeamSpot_cfi')

process.load("RecoEcal.Configuration.RecoEcal_cff")


process.load("RecoLocalCalo.EcalRecAlgos.EcalSeverityLevelESProducer_cfi")
process.load("RecoEcal.EgammaClusterProducers.ecalClusteringSequence_cff")
process.load("RecoEcal.EgammaCoreTools.EcalNextToDeadChannelESProducer_cff")
process.load("RecoEcal.EgammaClusterProducers.reducedRecHitsSequence_cff")

process.load("DQMServices.Core.DQM_cfg")

process.load("DQMServices.Components.DQMEnvironment_cfi")


process.load("DQM.EcalMonitorTasks.EcalMonitorTask_cfi")

process.load("DQM.EcalMonitorClient.EcalMonitorClient_cfi")


### Individual module setups ###

process.ecalPhysicsFilter = cms.EDFilter("EcalMonitorPrescaler",
    cosmics = cms.untracked.uint32(1),
    physics = cms.untracked.uint32(1),
    EcalRawDataCollection = cms.InputTag("ecalDigis")
)

process.MessageLogger = cms.Service("MessageLogger",
    cerr = cms.untracked.PSet(
        default = cms.untracked.PSet(
            limit = cms.untracked.int32(-1)
        ),
        EcalLaserDbService = cms.untracked.PSet(
            limit = cms.untracked.int32(10)
        ),
        noTimeStamps = cms.untracked.bool(True),
        threshold = cms.untracked.string('WARNING'),
        noLineBreaks = cms.untracked.bool(True)
    ),
    cout = cms.untracked.PSet(
        default = cms.untracked.PSet(
            limit = cms.untracked.int32(0)
        ),
        EcalDQM = cms.untracked.PSet(
            limit = cms.untracked.int32(-1)
        ),
        threshold = cms.untracked.string('INFO')
    ),
    categories = cms.untracked.vstring('EcalDQM', 
        'EcalLaserDbService'),
    destinations = cms.untracked.vstring('cerr', 
        'cout')
)

process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(hardcoded_maxEvents)
  # input = cms.untracked.int32(-1)
)

#FOLLOWING LINE?
process.es_prefer_GlobalTag = cms.ESPrefer('PoolDBESSource','GlobalTag')

process.ecalMonitorClient.verbosity = hardcoded_verbosity
process.ecalMonitorClient.workers = ['IntegrityClient', 'OccupancyClient', 'PresampleClient', 'RawDataClient', 'TimingClient', 'SelectiveReadoutClient', 'TrigPrimClient', 'SummaryClient']
process.ecalMonitorClient.workerParameters.SummaryClient.params.activeSources = ['Integrity', 'RawData', 'Presample', 'TriggerPrimitives', 'Timing', 'HotCell']
process.ecalMonitorClient.commonParameters.onlineMode = True

process.GlobalTag.toGet = cms.VPSet(cms.PSet(
    record = cms.string('EcalDQMChannelStatusRcd'),
    tag = cms.string('EcalDQMChannelStatus_v1_hlt'),
), 
    cms.PSet(
        record = cms.string('EcalDQMTowerStatusRcd'),
        tag = cms.string('EcalDQMTowerStatus_v1_hlt'),
    ))

# FOLLOWING toGet
# process.GlobalTag.toGet = cms.VPSet(
#     cms.PSet(
#         record = cms.string('EcalDQMChannelStatusRcd'),
#         tag = cms.string('EcalDQMChannelStatus_v1_hlt'),
#         connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
#         #connect = cms.string('sqlite_file:dqmMaskXTAL-ECAL_20160614.db')
#     ),
#     cms.PSet(
#         record = cms.string('EcalDQMTowerStatusRcd'),
#         tag = cms.string('EcalDQMTowerStatus_v1_hlt'),
#         connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS')
#         #connect = cms.string('sqlite_file:dqmMaskTT-ECAL_20160614.db')
#     )
# )

process.preScaler.prescaleFactor = hardcoded_prescaleFactor

# process.DQMStore.referenceFileName = "/dqmdata/dqm/reference/ecal_reference.root"

if (hardcoded_readRaw):
  process.source.runNumber = cms.untracked.uint32(hardcoded_runNumber)
  process.source.runInputDir = cms.untracked.string(hardcoded_inputPath)
  process.source.scanOnce = cms.untracked.bool(True)
  process.source.minEventsPerLumi = cms.untracked.int32(-1)
else:
  listOfInputFiles = []
  inputFileNamesFileObject = open(hardcoded_inputPath, 'r')
  for inputFileName in inputFileNamesFileObject:
    if (inputFileName[:5] != "file:" ):
      listOfInputFiles.append("root://cms-xrd-global.cern.ch/" + inputFileName.strip())
    else:
      listOfInputFiles.append(inputFileName.strip())
  process.source = cms.Source("PoolSource",
                              fileNames = cms.untracked.vstring(*tuple(listOfInputFiles))
  )
  lumisToProcess = []
  for lumiToProcess in hardcoded_lumisToProcess:
    lumisToProcess.append(cms.LuminosityBlockRange(hardcoded_runNumber, int(lumiToProcess), hardcoded_runNumber, int(lumiToProcess)))

  if (len(lumisToProcess) > 0): process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange(*tuple(lumisToProcess))
        
process.DQM = cms.Service("DQM",
    filter = cms.untracked.string(''),
    publishFrequency = cms.untracked.double(5.0),
    collectorHost = cms.untracked.string(''),
    collectorPort = cms.untracked.int32(0),
    debug = cms.untracked.bool(False)
)

process.dqmEnv.subSystemFolder = cms.untracked.string('Ecal')
process.dqmSaver.tag = cms.untracked.string('Ecal')
# process.dqmSaver.path = cms.untracked.string('/afs/cern.ch/work/t/tmudholk/public/DQMUploads/')
process.dqmSaver.path = cms.untracked.string('./')

process.dqmSaver.convention = "Offline"
process.dqmSaver.referenceHandling = "skip"
process.dqmSaver.version = 1
# process.dqmSaver.workflow = "/All/Run2017/CentralDAQ"
process.dqmSaver.workflow = hardcoded_workflow
# process.dqmSaver.workflow = "/All/Run2017SplashEventsTest/Evt%d"%(TMP_eventCounter + 1 + TMP_eventOffset)
# process.dqmSaver.workflow = "/All/Run2017SplashEventsWeightsSequence/Evt%d"%(TMP_eventCounter + 1 + TMP_eventOffset)

process.simEcalTriggerPrimitiveDigis.InstanceEB = "ebDigis"
process.simEcalTriggerPrimitiveDigis.InstanceEE = "eeDigis"
process.simEcalTriggerPrimitiveDigis.Label = "ecalDigis"

process.ecalMonitorTask.workers = ['ClusterTask', 'EnergyTask', 'IntegrityTask', 'OccupancyTask', 'RawDataTask', 'TimingTask', 'TrigPrimTask', 'PresampleTask', 'SelectiveReadoutTask']
process.ecalMonitorTask.verbosity = hardcoded_verbosity
process.ecalMonitorTask.collectionTags.EEBasicCluster = "multi5x5SuperClusters:multi5x5EndcapBasicClusters"
process.ecalMonitorTask.collectionTags.EESuperCluster = "multi5x5SuperClusters:multi5x5EndcapSuperClusters"
process.ecalMonitorTask.collectionTags.EBBasicCluster = "hybridSuperClusters:hybridBarrelBasicClusters"
process.ecalMonitorTask.collectionTags.EBSuperCluster = "correctedHybridSuperClusters"
process.ecalMonitorTask.collectionTags.Source = "rawDataCollector"
process.ecalMonitorTask.collectionTags.TrigPrimEmulDigi = "simEcalTriggerPrimitiveDigis"
process.ecalMonitorTask.workerParameters.TrigPrimTask.params.runOnEmul = True
process.ecalMonitorTask.commonParameters.willConvertToEDM = False
process.ecalMonitorTask.commonParameters.onlineMode = True

process.reducedEcalRecHitsEB.interestingDetIdCollections = [cms.InputTag("interestingEcalDetIdEB")]

# process.ecalRecHit.EEuncalibRecHitCollection = cms.InputTag("ecalWeightUncalibRecHit", "EcalUncalibRecHitsEE")
# process.ecalRecHit.EBuncalibRecHitCollection = cms.InputTag("ecalWeightUncalibRecHit", "EcalUncalibRecHitsEB")

# process.particleFlowSuperClusterECAL.useRegression = False
# process.particleFlowSuperClusterECAL.use_preshower = False

### Sequences ###

process.ecalPreRecoSequence = cms.Sequence(process.bunchSpacingProducer + process.ecalDigis)
# process.ecalPreRecoSequence = cms.Sequence(process.bunchSpacingProducer + process.ecalDigis + process.ecalPreshowerDigis)

# process.ecalRecoSequence = cms.Sequence((process.ecalMultiFitUncalibRecHit+process.ecalDetIdToBeRecovered+process.ecalRecHit+process.ecalPreshowerRecHit)+(process.simEcalTriggerPrimitiveDigis+process.gtDigis)+(process.particleFlowRecHitPS*process.particleFlowClusterPS*process.particleFlowRecHitECAL*process.particleFlowClusterECALUncorrected*process.particleFlowClusterECAL*process.offlineBeamSpot*process.particleFlowSuperClusterECAL))
# process.ecalRecoSequence = cms.Sequence((process.ecalMultiFitUncalibRecHit+process.ecalDetIdToBeRecovered+process.ecalRecHit)+(process.simEcalTriggerPrimitiveDigis+process.gtDigis)+(process.particleFlowRecHitECAL*process.particleFlowClusterECALUncorrected*process.particleFlowClusterECAL*process.offlineBeamSpot*process.particleFlowSuperClusterECAL))
process.ecalRecoSequence = cms.Sequence((process.ecalMultiFitUncalibRecHit+process.ecalDetIdToBeRecovered+process.ecalRecHit)+(process.simEcalTriggerPrimitiveDigis+process.gtDigis)+(process.hybridClusteringSequence+process.multi5x5ClusteringSequence))
# process.ecalRecoSequence = cms.Sequence((process.ecalWeightUncalibRecHit+process.ecalDetIdToBeRecovered+process.ecalRecHit)+(process.simEcalTriggerPrimitiveDigis+process.gtDigis)+(process.hybridClusteringSequence+process.multi5x5ClusteringSequence))
process.multi5x5ClusteringSequence = cms.Sequence(process.multi5x5BasicClustersCleaned+process.multi5x5SuperClustersCleaned+process.multi5x5BasicClustersUncleaned+process.multi5x5SuperClustersUncleaned+process.multi5x5SuperClusters)
process.hybridClusteringSequence = cms.Sequence(process.cleanedHybridSuperClusters+process.uncleanedHybridSuperClusters+process.hybridSuperClusters+process.correctedHybridSuperClusters+process.uncleanedOnlyCorrectedHybridSuperClusters)

### Paths ###

process.ecalMonitorPath = cms.Path(process.preScaler+process.ecalPreRecoSequence+process.ecalPhysicsFilter+process.ecalRecoSequence+process.ecalMonitorTask)
process.ecalClientPath = cms.Path(process.preScaler+process.ecalPreRecoSequence+process.ecalPhysicsFilter+process.ecalMonitorClient)

process.dqmEndPath = cms.EndPath(process.dqmEnv)
process.dqmOutputPath = cms.EndPath(process.dqmSaver)

### Schedule ###

process.schedule = cms.Schedule(process.ecalMonitorPath,process.ecalClientPath,process.dqmEndPath,process.dqmOutputPath)

### Run type specific ###

# runTypeName = process.runType.getRunTypeName()
# if runTypeName == 'hi_run':
#   process.ecalMonitorTask.collectionTags.Source = "rawDataRepacker"
#   process.ecalDigis.InputLabel = cms.InputTag('rawDataRepacker')

#FOLLOWING
# referenceFileName = process.DQMStore.referenceFileName.pythonValue()
# runTypeName = process.runType.getRunTypeName()
# if (runTypeName == 'pp_run' or runTypeName == 'pp_run_stage1'):
#     process.DQMStore.referenceFileName = referenceFileName.replace('.root', '_pp.root')
# elif (runTypeName == 'cosmic_run' or runTypeName == 'cosmic_run_stage1'):
#     process.DQMStore.referenceFileName = referenceFileName.replace('.root', '_cosmic.root')
# #    process.dqmEndPath.remove(process.dqmQTest)
#     process.ecalMonitorTask.workers = ['EnergyTask', 'IntegrityTask', 'OccupancyTask', 'RawDataTask', 'TimingTask', 'TrigPrimTask', 'PresampleTask', 'SelectiveReadoutTask']
#     process.ecalMonitorClient.workers = ['IntegrityClient', 'OccupancyClient', 'PresampleClient', 'RawDataClient', 'TimingClient', 'SelectiveReadoutClient', 'TrigPrimClient', 'SummaryClient']
#     process.ecalMonitorClient.workerParameters.SummaryClient.params.activeSources = ['Integrity', 'RawData', 'Presample', 'TriggerPrimitives', 'Timing', 'HotCell']
#     process.ecalMonitorTask.workerParameters.PresampleTask.params.doPulseMaxCheck = False 
# elif runTypeName == 'hi_run':
#     process.DQMStore.referenceFileName = referenceFileName.replace('.root', '_hi.root')
#     process.ecalMonitorTask.collectionTags.Source = "rawDataRepacker"
#     process.ecalDigis.InputLabel = cms.InputTag('rawDataRepacker')
# elif runTypeName == 'hpu_run':
#     process.DQMStore.referenceFileName = referenceFileName.replace('.root', '_hpu.root')
#     process.source.SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('*'))


### process customizations included here
from DQM.Integration.config.online_customizations_cfi import *
process = customise(process)
