import names
import random
import hashlib
import jsonpickle

import crypto
import consts

from consts import Color as color

# Define an exception that inherits Exception
class GhostpassException(Exception):
    def __init__(self, message):
        print "[!] Error: ", color.R, message, color.W
        exit(1)


'''
Initalization Process

1. Initialize new object
2. Initalize new state with master password and corpus file
3. Perform preemptive password encryption with master password and corpus
4. Save state as JSON in .config/ghostpass TODO: maybe merkle tree??

'''
class Ghostpass(object):

    # represents global pseudorandom identifying ID for session
    uuid = names.get_first_name() + names.get_first_name() + str(random.randrange(0, 100))

    def __init__(self):
        '''
        initializes the state of the new object, and creates the instance variables we need
        '''
        self.state = 1 # activation state
        self.password = None # represents master password

    def _decorator(func):
        '''
        decorator method that encapsulates other instance methods, checking to see
        if the activation state permits execution
        '''
        def state_check(self, *params):

            # check if the session is actually initialized
            if self.state != 1:
                raise GhostpassException("session is marked as inactive / uninitialized")
                return None

            # pass positional args, since instance methods all have different parameters
            return func(self, *params)
        return state_check


    @_decorator
    def init_state(self, password, corpus_path):
        '''
        initializes the new session, immediately hashing the master password
        and loading the corpus
        '''

        # perform error-checking and hash using SHA512
        if password == "":
            raise GhostpassException("master password is not optional")
        self.password = hashlib.sha512(password).hexdigest()

        # convert path into Markov-chain cipher
        if corpus_path == "":
            raise GhostpassException("corpus path is not optional")

        # generate markov chain cipher
        self.markov = crypto.MarkovHelper(corpus_path)
        self.markov.add_text()

        # since cleartext password is copied to object, make sure to delete
        del password

        return 0

    @_decorator
    def export(self):

        # Export to new JSON file
        with open(consts.DEFAULT_CONFIG_PATH + "/" + self.uuid + ".json", "w+") as f:
            f.write(jsonpickle.encode(self))
        f.close()
        return 0
