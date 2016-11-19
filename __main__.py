#!/usr/bin/env python3

from ApplicationStore import ApplicationStore
from EventStore import EventStore
from FileStore import FileStore
from PreloadLoggerLoader import PreloadLoggerLoader
from SqlLoader import SqlLoader
from UserConfigLoader import UserConfigLoader
from PolicyEngine import PolicyEngine
from LibraryPolicies import OneLibraryPolicy, CompoundLibraryPolicy
from constants import DATAPATH, DATABASENAME, USERCONFIGPATH
import getopt
import sys
from utils import __setCheckMissing, __setDebug, __setOutputFs, \
                  checkMissingEnabled, debugEnabled, outputFsEnabled

USAGE_STRING = 'Usage: __main__.py [--check-missing --help --debug ' \
               '--output-fs=<DIR>]'


# Main function
# @profile
def main(argv):
    # Parse command-line parameters
    try:
        (opts, args) = getopt.getopt(argv, "hcdf:", ["help", "check-missing",
                                                     "debug", "output-fs="])
    except(getopt.GetoptError):
        print(USAGE_STRING)
        sys.exit(2)
    else:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print(USAGE_STRING)
                sys.exit()
            elif opt in ('c', '--check-missing'):
                __setCheckMissing(True)
            elif opt in ('-d', '--debug'):
                __setDebug(True)
            elif opt in ('-f', '--output-fs'):
                if not arg:
                    print(USAGE_STRING)
                    sys.exit(2)
                __setOutputFs(arg[1:] if arg[0] == '=' else arg)

    # Make the application, event and file stores
    store = ApplicationStore.get()
    evStore = EventStore.get()
    fileStore = FileStore.get()

    # Load up user-related variables
    userConf = UserConfigLoader(USERCONFIGPATH)

    # Load up and check the SQLite database
    sql = None
    print("\nLoading the SQLite database: %s..." % (DATAPATH+DATABASENAME))
    try:
        sql = SqlLoader(DATAPATH+DATABASENAME)
    except ValueError as e:
        print("Failed to parse SQL: %s" % e.args[0], file=sys.stderr)
        sys.exit(-1)
    if checkMissingEnabled():
        print("Checking for missing application identities...")
        sql.listMissingActors()
    sql.loadDb(store)
    print("Loaded the SQLite database.")

    # Load up the PreloadLogger file parser
    print("\nLoading the PreloadLogger logs in folder: %s..." % DATAPATH)
    pll = PreloadLoggerLoader(DATAPATH)
    if checkMissingEnabled():
        print("Checking for missing application identities...")
        pll.listMissingActors()
    pll.loadDb(store)
    print("Loaded the PreloadLogger logs.")

    # Sort all the events in found Applications
    print("\nSorting all events...")
    evStore.sort()
    print("Sorted all %d events in the event store." % evStore.getEventCount())

    # Simulate the events to build a file model
    print("\nSimulating all events to build a file model...")
    evStore.simulateAllEvents()
    print("Simulated all events.")

    # Print the model as proof of concept
    if debugEnabled():
        print("\nPrinting the file model...\n")
        fileStore.printFiles(showDeleted=True,
                             showCreationTime=True,
                             showDocumentsOnly=True,
                             userHome=userConf.getSetting("HomeDir"),
                             showDesignatedOnly=False)

    # Make the filesystem corresponding to the model
    if outputFsEnabled():
        print("\nMaking a copy of the file model at '%s'...\n" %
              outputFsEnabled())
        fileStore.makeFiles(outputDir=outputFsEnabled(),
                            showDeleted=True,
                            showDocumentsOnly=True,
                            userHome=userConf.getSetting("HomeDir"),
                            showDesignatedOnly=False)

    # Policy engine. Create a policy and run a simulation to score it.
    engine = PolicyEngine()

    print("\nRunning the One Library policy...")
    engine.runPolicy(OneLibraryPolicy(userConf=userConf),
                     outputDir=outputFsEnabled())

    print("\nRunning the Compound Library policy...")
    engine.runPolicy(CompoundLibraryPolicy(userConf=userConf),
                     outputDir=outputFsEnabled())


if __name__ == "__main__":
    main(sys.argv[1:])
