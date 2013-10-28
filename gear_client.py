import gear
import simplejson
import uuid
import time
import argparse
import sys

# simple python client
# usage:
#  To run a build:
#      python gear_client.py -s MyGearmanSever --function=build:myProject \
#            --params='{"OFFLINE_NODE_WHEN_COMPLETE":"false","param1":"moon","param1":"sun"}'
#
#  To stop/abort a build:
#      python gear_client.py -s MyGearmanSever --function=stop:jenkins-server2.novalocal \
#            --params='{"name":"guava","number":"130"}'
#
#  To change the build description:
#      python gear_client.py -s MyGearmanSever --function=set_description:jenkins-server2.novalocal \
#            --params='{"name":"guava","number":"105","html_description":"<h1>new description</h1>"}'
    
class Client(object):
    def __init__(self):
        self.args = None
        self.config = None
        
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Gearman Client')
        parser.add_argument('-s', dest='server',
                            default='localhost',
                            help='Gearman server host (default=localhost)')
        parser.add_argument('-p', dest='port', default=4730,
                            help='Gearman server port (default=4730)')
        parser.add_argument('--wait', action='store_true',
                            help='Wait for all jobs to complete')
        parser.add_argument('--function', dest='function',
                            help='Gearman function')
        parser.add_argument('--jobs', dest='jobs', default=1,
                            help='Number of jobs (default=1)')
        parser.add_argument('--params', dest='params', 
                            default={"OFFLINE_NODE_WHEN_COMPLETE":"false"},
                            help='Parameters to pass to build')
        parser.add_argument('--log-config', dest='log_config',
                            help='logging config file')
        self.args = parser.parse_args()

    def main(self):
        gclient = gear.Client()
        gclient.addServer(self.args.server)
        gclient.waitForServer()  # Wait for at least one server to be connected

        print time.asctime( time.localtime(time.time()))
        if not isinstance(self.args.params, dict):
            build_params = simplejson.loads(self.args.params)
        else:
            build_params = self.args.params
            
        for x in range(0, int(self.args.jobs)):
            job_id = uuid.uuid4().hex
            build_params.update({'uuid':job_id})
            gjob = gear.Job(self.args.function, 
                           simplejson.dumps(build_params), 
                           unique=job_id)
            print "Sending job "+self.args.function+" to "+self.args.server+" with params="+ str(build_params)
            gclient.submitJob(gjob)
        
        # wait for last job to complete before exiting
        if self.args.wait:
            finished = False
            while True:
                if (gjob.complete):
                    finished = True
                time.sleep(1);
                if finished:
                    break

        print time.asctime( time.localtime(time.time()) )

def main():
    client = Client()
    client.parse_arguments()
    client.main()

if __name__ == '__main__':
    sys.path.insert(0, '.')
    main()
            
