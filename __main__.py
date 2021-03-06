#!/usr/bin/env python3

from ApplicationStore import ApplicationStore
from AttackSimulator import AttackSimulator
from Event import dbgPrintExcludedEvents
from EventStore import EventStore
from FileStore import FileStore
from PreloadLoggerLoader import PreloadLoggerLoader
from SqlLoader import SqlLoader
from UserConfigLoader import UserConfigLoader
from GraphEngine import GraphEngine
from PolicyEngine import PolicyEngine
from FrequentFileEngine import FrequentFileEngine
from LibraryManager import LibraryManager
from Policies import OneLibraryPolicy, CompoundLibraryPolicy, UnsecurePolicy, \
                     FileTypePolicy, DesignationPolicy, FolderPolicy, \
                     OneFolderPolicy, DistantFolderPolicy, FilenamePolicy, \
                     OneDistantFolderPolicy, FutureAccessListPolicy, \
                     StickyBitPolicy, CustomLibraryPolicy, \
                     Win8Policy, Win10Policy, ProtectedFolderPolicy, \
                     LibraryFolderPolicy, RemovableMediaPolicy, \
                     FolderFilenamePolicy, FolderRestrictedAppsPolicy, \
                     CompositionalPolicy, HSecurePolicy, HBalancedPolicy, \
                     HBalancedSecuredPolicy, FolderSecuredPolicy, \
                     HUsableSecuredPolicy
from constants import DATABASENAME, USERCONFIGNAME
from utils import __setCheckMissing, __setDebug, __setOutputFs, \
                  __setRelatedFiles, __setScore, __setGraph, __setAttacks, \
                  __setPrintClusters, __setUser, __setCheckExcludedFiles, \
                  __setPlottingDisabled, __setSkip, __setPrintExtensions, \
                  __setFrequency, \
                  checkMissingEnabled, debugEnabled, outputFsEnabled, \
                  relatedFilesEnabled, scoreEnabled, graphEnabled, \
                  printClustersEnabled, checkExcludedFilesEnabled, \
                  skipEnabled, attacksEnabled, printExtensions, \
                  initMimeTypes, getDataPath, registerTimePrint, tprnt
import getopt
import sys
import os
import mimetypes

USAGE_STRING = 'Usage: __main__.py [--user=<NAME> --check-excluded-files ' \
               '--check-missing --score\n\t\t--skip=<Policy,Policy,\'graphs' \
               '\'> --clusters --graph --extensions\n\t\t--disable-plotting ' \
               '--attacks --related-files --frequency\n\t\t--output=<DIR> ' \
               '--debug] ' \
               '\n\nor:     __main__.py --inode=<INODE> [--user=<NAME> ' \
               '--debug]' \
               '\n\nor:     __main__.py --post-analysis=<DIR,DIR,DIR> ' \
               '[--related-files --debug]'\
               '\n\nor:     __main__.py --help'


# Main function
# @profile
def main(argv):
    __opt_inode_query = None
    __opt_post_analysis = None
    __opt_quick_pol = None

    # Parse command-line parameters
    try:
        (opts, args) = getopt.getopt(argv, "hta:cedf:o:q:sk:rpgGi:u:x",
                                     ["help",
                                      "attacks",
                                      "post-analysis=",
                                      "check-missing",
                                      "check-excluded-files",
                                      "debug",
                                      "frequency",
                                      "inode",
                                      "extensions",
                                      "related-files",
                                      "output=",
                                      "output-fs=",
                                      "score",
                                      "quick-pol=",
                                      "skip=",
                                      "user",
                                      "clusters",
                                      "print-clusters",
                                      "graph",
                                      "graph-clusters",
                                      "disable-plotting"])
    except(getopt.GetoptError):
        print(USAGE_STRING)
        sys.exit(2)
    else:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print(USAGE_STRING + "\n\n\n\n")

                print("--attacks:\n\tSimulates attacks and reports "
                      "on proportions of infected files and apps.\n")
                print("--check-excluded-files:\n\tPrints the lists of files "
                      "accessed by apps that also wrote to excluded\n\tfiles,"
                      " then aborts execution of the program.\n")
                print("--check-missing:\n\tChecks whether some Desktop IDs "
                      "for apps in the user's directory are\n\tmissing. If so,"
                      " aborts execution of the program.\n")
                print("--clusters:\n\tPrints clusters of files with "
                      "information flows to one another. Requires\n\tthe "
                      "--score option.\n")
                print("--debug:\n\tPrints additional debug information in "
                      "various code paths to help debug\n\tthe program.\n")
                print("--disable-plotting:\n\tDo not plot cluster graphs. See "
                      "the --graph option.\n")
                print("--extensions:\n\tPrints file extensions and MIME type "
                      "associations for this user.\n")
                print("--frequency:\n\tSets the frequency used by the "
                      "frequent-itemsets algorithm in the\n\t--related-files "
                      "post-analysis. Requires the --related-files option.\n")
                print("--graph:\n\tFind communities in file/app "
                      "accesses using graph theory methods.\n")
                print("--help:\n\tPrints this help information and exits.\n")
                print("--output=<DIR>:\n\tSaves a copy of the simulated "
                      "files, and some information on events\n\trelated to "
                      "them, in a folder created at the <DIR> path.\n")
                print("--post-analysis=<DIR,DIR,DIR>:\n\t"
                      "Uses the value pointed to"
                      " by --output in order to produce graphs and\n\t"
                      "statistics.\n")
                print("--quick-pol=Policy:\n\tReplace the default policies "
                      "with this one single Policy.\n")
                print("--related-files:\n\tMines for files that are frequently"
                      " accessed together by apps. Produces\n\toutput files in"
                      " scoring mode, and an analysis output in post-analysis"
                      "\n\tmode. See also --frequency.\n")
                print("--score:\n\tCalculates the usability and security "
                      "scores of a number of file access\n\tcontrol policies"
                      ", replayed over the simulated accesses. Prints results"
                      "\n\tand saves them to the output directory.\n")
                print("--skip=<Policy,Policy,'graphs'>:\n\tSkip the scoring of "
                      "policies in the lists. If the list contains the word"
                      "\n\t'graphs', skips the general graph computation.\n")
                sys.exit()
            elif opt in ('-c', '--check-missing'):
                __setCheckMissing(True)
            elif opt in ('-e', '--check-excluded-files'):
                __setCheckExcludedFiles(True)
            elif opt in ('-x', '--extensions'):
                __setPrintExtensions(True)
            elif opt in ('-d', '--debug'):
                __setDebug(True)
            elif opt in ('-r', '--related-files'):
                __setRelatedFiles(True)
            elif opt in ('-s', '--score'):
                __setScore(True)
            elif opt in ('-p', '--print-clusters', '--clusters'):
                __setPrintClusters(True)
            elif opt in ('-g', '--graph-clusters', '--graph'):
                __setGraph(True)
            elif opt in ('-t', '--attacks'):
                __setAttacks(True)
            elif opt in ('-G', '--disable-plotting'):
                __setPlottingDisabled(True)
            elif opt in ('-f', '--frequency'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __setFrequency(arg[1:] if arg[0] == '=' else arg)
            elif opt in ('-o', '--output-fs', '--output'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __setOutputFs(arg[1:] if arg[0] == '=' else arg)
            elif opt in ('-u', '--user'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __setUser(arg[1:] if arg[0] == '=' else arg)
            elif opt in ('-i', '--inode'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                try:
                    __opt_inode_query = (arg[1:] if arg[0] == '=' else arg)
                except(ValueError) as e:
                    print(USAGE_STRING)
                    sys.exit(2)
            elif opt in ('-a', '--post-analysis'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __opt_post_analysis = (arg[1:] if arg[0] == '=' else arg)
            elif opt in ('-q', '--quick-pol'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __opt_quick_pol = (arg[1:] if arg[0] == '=' else arg)
            elif opt in ('-k', '--skip'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __opt_skip = (arg[1:] if arg[0] == '=' else arg)
                __setSkip(__opt_skip.split(","))

    registerTimePrint()

    if __opt_post_analysis:
        if relatedFilesEnabled():
            tprnt("Starting post-analysis of related files...\n")
            engine = FrequentFileEngine()
            engine.processFrequentItemLists(__opt_post_analysis)

        else:
            tprnt("Starting post-analysis of usability/security scores...\n")
            from AnalysisEngine import AnalysisEngine
            if outputFsEnabled():
                engine = AnalysisEngine(inputDir=__opt_post_analysis,
                                        outputDir=outputFsEnabled())
            else:
                engine = AnalysisEngine(inputDir=__opt_post_analysis)
            engine.analyse()

        sys.exit(0)

    # Make the application, event and file stores
    store = ApplicationStore.get()
    evStore = EventStore.get()
    fileStore = FileStore.get()
    initMimeTypes()
    datapath = getDataPath()

    # Load up user-related variables
    userConf = UserConfigLoader.get(path=datapath+USERCONFIGNAME)

    # Load up and check the SQLite database
    sql = None
    tprnt("\nLoading the SQLite database: %s..." % (datapath+DATABASENAME))
    try:
        sql = SqlLoader(datapath+DATABASENAME)
    except ValueError as e:
        print("Failed to parse SQL: %s" % e.args[0], file=sys.stderr)
        sys.exit(-1)
    if checkMissingEnabled():
        tprnt("Checking for missing application identities...")
        sql.listMissingActors()
    sql.loadDb(store)
    sqlAppCount = sql.appCount
    sqlInstCount = sql.instCount
    sqlEvCount = sql.eventCount
    sqlValidEvCount = sql.validEventRatio
    tprnt("Loaded the SQLite database.")

    # Load up the PreloadLogger file parser
    tprnt("\nLoading the PreloadLogger logs in folder: %s..." % datapath)
    pll = PreloadLoggerLoader(datapath)
    if checkMissingEnabled():
        tprnt("Checking for missing application identities...")
        pll.listMissingActors()
    pll.loadDb(store)
    pllAppCount = pll.appCount
    pllInstCount = pll.instCount
    pllEvCount = pll.eventCount
    pllValidEvCount = pll.validEventRatio
    tprnt("Loaded the PreloadLogger logs.")

    # Resolve actor ids in all apps' events
    tprnt("\nUsing PreloadLogger Applications to resolve interpreters in "
          "Zeitgeist Applications...")
    (interpretersAdded, instancesEliminated) = store.resolveInterpreters()
    tprnt("Resolved interpreter ids in %d Applications, and removed %d "
          "instances by merging them with another as a result." % (
           interpretersAdded, instancesEliminated))

    # Update events' actor ids in the ApplicationStore, then take them and send
    # them to the EvnetStore. Finally, sort the EventStore by timestamp.
    tprnt("\nInserting and sorting all events...")
    store.sendEventsToStore()
    evStore.sort()
    evCount = evStore.getEventCount()
    tprnt("Sorted all %d events in the event store." % evCount)

    # Simulate the events to build a file model
    tprnt("\nSimulating all events to build a file model...")
    evStore.simulateAllEvents()
    del sql
    del pll
    evStore.sort()
    tprnt("Simulated all events. %d files initialised." % len(fileStore))

    appCount = store.getAppCount()
    userAppCount = store.getUserAppCount()
    instCount = len(store)
    userInstCount = store.getUserInstCount()
    fileCount = len(fileStore)
    docCount = fileStore.getUserDocumentCount(userConf.getSetting("HomeDir"))
    
    if printExtensions():
        exts = set()
        for f in fileStore:
            exts.add(f.getExtension())
        try:
            exts.remove(None)
        except(KeyError):
            pass
        tprnt("Info: the following file extensions were found:")
        for e in sorted(exts):
            print("\t%s: %s" % (e, mimetypes.guess_type("f.%s" % e, strict=False)))

        if checkExcludedFilesEnabled():
            tprnt("\nPrinting files written and read by instances which wrote"
                  "to excluded directories...")
            dbgPrintExcludedEvents()
        import time as t
        t.sleep(10)

    # Manage --inode queries
    if __opt_inode_query:
        inodes = __opt_inode_query.split(",")
        for inode in sorted(int(i) for i in inodes):
            f = fileStore.getFile(inode)
            tprnt("\nInode queried: %d" % inode)
            tprnt("Corresponding file: %s\n\t(%s)" % (f.getName(), f))
        sys.exit(0)

    # Print the model as proof of concept
    if debugEnabled():
        tprnt("\nPrinting the file model...\n")
        fileStore.printFiles(showDeleted=True,
                             showCreationTime=True,
                             showDocumentsOnly=True,
                             userHome=userConf.getSetting("HomeDir"),
                             showDesignatedOnly=False)

    # Make the filesystem corresponding to the model
    if outputFsEnabled():
        tprnt("\nMaking a copy of the file model at '%s'...\n" %
              outputFsEnabled())
        fileStore.makeFiles(outputDir=outputFsEnabled(),
                            showDeleted=True,
                            showDocumentsOnly=False,
                            userHome=userConf.getSetting("HomeDir"),
                            showDesignatedOnly=False)

        with open(os.path.join(outputFsEnabled(), "statistics.txt"), "w") as f:
            msg = "SQL: %d apps; %d instances; %d events; %d%% valid\n" % \
                  (sqlAppCount, sqlInstCount, sqlEvCount, sqlValidEvCount)
            msg += "PreloadLogger: %d apps; %d instances; %d events; " \
                   "%d%% valid\n" % \
                  (pllAppCount, pllInstCount, pllEvCount, pllValidEvCount)
            msg += "Simulated: %d apps; %d instances; %d user apps; %d user" \
                   " instances; %d events; %d files; %d user documents\n" % \
                  (appCount, instCount, userAppCount, userInstCount,
                   evCount, fileCount, docCount)
            exclLists = userConf.getDefinedSecurityExclusionLists()
            for l in exclLists:
                msg += "Exclusion list '%s' defined.\n" % l
            print(msg, file=f)

    # Build a general access graph.
    if graphEnabled():
        skipList = skipEnabled()
        if skipList and 'graphs' in skipList:
            tprnt("\nGraphs in skip list, skipping global graph generation.")
        else:
            engine = GraphEngine.get()
            engine.runGraph(policy=None)

    # Policy engine. Create a policy and run a simulation to score it.
    if scoreEnabled() or attacksEnabled() or graphEnabled():
        engine = PolicyEngine()

        if __opt_quick_pol:
            policies = [__opt_quick_pol]
            polArgs = [None]
        else:
            policies = [CompoundLibraryPolicy,
                        CustomLibraryPolicy,
                        DesignationPolicy,
                        DistantFolderPolicy,

                        FilenamePolicy,
                        FileTypePolicy,
                        FolderPolicy,

                        OneDistantFolderPolicy,
                        OneFolderPolicy,
                        OneLibraryPolicy,
                        UnsecurePolicy,

                        Win10Policy,
                        Win8Policy,

                        HSecurePolicy,
                        HBalancedPolicy,

                       'HSecureSbPolicy',
                       'HSecureSbFaPolicy',
                       'HSecureFaPolicy',

                       'HBalancedSbPolicy',
                       'HBalancedSbFaPolicy',
                       'HBalancedFaPolicy',
                       
                       'OneDistantFolderSbPolicy',
                       'OneDistantFolderSbFaPolicy',
                       'OneDistantFolderFaPolicy',
                       'HUsableSecuredSbPolicy',
                       'HUsableSecuredSbFaPolicy',
                       'HUsableSecuredFaPolicy',

                       'HBalancedSecuredSbPolicy',
                       'HBalancedSecuredSbFaPolicy',
                       'HBalancedSecuredFaPolicy',
                       'DistantFolderSbPolicy',
                       'DistantFolderSbFaPolicy',
                       'DistantFolderFaPolicy',

                       'LibraryFolderSbPolicy',
                       'LibraryFolderSbFaPolicy',
                       'LibraryFolderFaPolicy',
                       'FileTypeSbPolicy',
                       'FileTypeSbFaPolicy',
                       'FileTypeFaPolicy',

                       'OneFolderSbPolicy',
                       'OneFolderSbFaPolicy',
                       'OneFolderFaPolicy',
                       'FolderSbPolicy',
                       'FolderSbFaPolicy',
                       'FolderFaPolicy',

                       'OneLibrarySbPolicy',
                       'OneLibrarySbFaPolicy',
                       'OneLibraryFaPolicy',
                       'CompoundLibrarySbPolicy',
                       'CompoundLibrarySbFaPolicy',
                       'CompoundLibraryFaPolicy',

                       'CustomLibrarySbPolicy',
                       'CustomLibrarySbFaPolicy',
                       'CustomLibraryFaPolicy',
                        ]

            polArgs = [None,
                       None,
                       None,
                       None,

                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,

                       None,
                       None,

                       None,
                       None,

                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,
                       None,
                       None,

                       None,
                       None,
                       None,
                       None,
                       None,
                       None,
                       ]
            # dict(folders=["~/Downloads", "/tmp"])

        skipList = skipEnabled()
        for (polIdx, polName) in enumerate(policies):
            pol = None
            arg = polArgs[polIdx]

            # Names with certain suffixes are dynamically generated policies.
            if isinstance(polName, str):
                if polName.endswith('SbPolicy'):
                    pols = [getattr(sys.modules[__name__], polName[:-8]+'Policy'),
                            StickyBitPolicy]
                    args = [arg,
                            dict(folders=["~", "/media", "/mnt"])]
                    pol = CompositionalPolicy(pols, args, polName)
                elif polName.endswith('SbFaPolicy'):
                    pols = [getattr(sys.modules[__name__], polName[:-10]+'Policy'),
                            StickyBitPolicy,
                            FutureAccessListPolicy]
                    args = [arg,
                            dict(folders=["~", "/media", "/mnt"]),
                            None]
                    pol = CompositionalPolicy(pols, args, polName)
                elif polName.endswith('FaPolicy'):
                    pols = [getattr(sys.modules[__name__], polName[:-8]+'Policy'),
                            FutureAccessListPolicy]
                    args = [arg,
                            None]
                    pol = CompositionalPolicy(pols, args, polName)
                # A normal policy, just invoke it directly.
                else:
                    polName = getattr(sys.modules[__name__], polName)

            # Existing policies, with arguments / or normal policies passed as
            # strings, including via the --quick flag.
            if not pol:
                pol = polName(**arg) if arg else polName()

            tprnt("\nRunning %s..." % pol.name)

            if skipList and pol.name in skipList:
                tprnt("%s is in skip list, skipping." % pol.name)
                continue

            engine.runPolicy(pol,
                             outputDir=outputFsEnabled(),
                             printClusters=printClustersEnabled())

            if pol.name == "FileTypePolicy" and checkMissingEnabled():
                pol.abortIfUnsupportedExtensions()

            if attacksEnabled():
                tprnt("Simulating attacks on %s..." % pol.name)
                sim = AttackSimulator(seed=0)
                sim.runAttacks(pol, outputDir=outputFsEnabled() or "/tmp/")

            del pol

    # Calculate frequently co-accessed files:
    if relatedFilesEnabled():
        engine = FrequentFileEngine()

        tprnt("\nMining for frequently co-accessed file types...")
        engine.mineFileTypes()


if __name__ == "__main__":
    main(sys.argv[1:])
