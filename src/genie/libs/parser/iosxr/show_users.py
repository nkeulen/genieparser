""" show_users.py

IOSXR parsers for the following commands:

    * 'show users'

"""

# Python
import re

# Genie
from genie.libs.parser.utils.common import Common
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Any, Optional

# ================================
# Schema for 'show users'
# ================================
class ShowUsersSchema(MetaParser):
    ''' Schema for:
            * 'show users'
    '''

    schema = {                
            Any(): {
                    'current_user': bool,
                    'user': str,
                    'service': str,
                    'conns': int,
                    'idle': str,
                    Optional('location'): str
                }
    }


# ================================
# Parser for 'show users'
# ================================
class ShowUsers(ShowUsersSchema):
    cli_command = 'show users'

    '''
    Sample output for "show users":

        Line            User                 Service  Conns   Idle        Location
        con0/0/CPU0     pyats                hardware     0  00:12:36     
        vty0            pyats                ssh          0  00:11:45     10.0.0.53
        vty1            cisco                ssh          0  00:12:38     10.0.0.54
        vty2            pyats                ssh          0  00:12:37     10.0.0.55
     *  vty3            cisco                ssh          0  00:00:00     10.0.0.56

    ''' 

    def cli(self, output=None):

        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output        

        # init result variable
        users_dict = {}     

        # table headers
        p0 = re.compile('^Line\s+User\s+Service.*?$')

        # current user on console
        p1 = re.compile('^\*\s+(?P<line>con\S+)\s+' + 
                        '(?P<user>\S+)\s+' + 
                        '(?P<service>\S+)\s+' + 
                        '(?P<conns>\d+)\s+' + 
                        '(?P<idle>\S+)$')

        # current user on remote
        p2 = re.compile('^\*\s+(?P<line>\S+)\s+' + 
                        '(?P<user>\S+)\s+' + 
                        '(?P<service>\S+)\s+' + 
                        '(?P<conns>\S+)\s+' + 
                        '(?P<idle>\S+)\s+' + 
                        '(?P<location>\S+)$')

        # not current user on console
        p3 = re.compile('^(?P<line>con\S+)\s+' + 
                        '(?P<user>\S+)\s+' + 
                        '(?P<service>\S+)\s+' + 
                        '(?P<conns>\d+)\s+' + 
                        '(?P<idle>\S+)$')

        # not current user on remote
        p4 = re.compile('^(?P<line>\S+)\s+' + 
                        '(?P<user>\S+)\s+' + 
                        '(?P<service>\S+)\s+' + 
                        '(?P<conns>\S+)\s+' + 
                        '(?P<idle>\S+)\s+' + 
                        '(?P<location>\S+)$')

        for line in out.splitlines():
            #print(f"Doing line:\n{line}\n")
            line = line.strip()

            # header line (ignored)
            m = p0.match(line)
            if m:
                continue    

            # current user on console
            m = p1.match(line)
            if m:
                user_dict = m.groupdict()
                user_dict['current_user'] = True
                line = user_dict['line']
                user_dict['conns'] = int(user_dict['conns'])
                user_line = user_dict['line']
                users_dict[user_line] = user_dict
                del user_dict['line']
                continue

            # current user on remote
            m = p2.match(line)
            if m:
                user_dict = m.groupdict()
                user_dict['current_user'] = True
                user_dict['conns'] = int(user_dict['conns'])
                user_line = user_dict['line']
                users_dict[user_line] = user_dict
                del user_dict['line']
                continue

            # not current user on console
            m = p3.match(line)
            if m:
                user_dict = m.groupdict()
                user_dict['current_user'] = False
                user_dict['conns'] = int(user_dict['conns'])
                user_line = user_dict['line']
                users_dict[user_line] = user_dict
                del user_dict['line']
                continue

            # not current user on remote
            m = p4.match(line)
            if m:
                user_dict = m.groupdict()
                user_dict['current_user'] = False
                user_dict['conns'] = int(user_dict['conns'])
                user_line = user_dict['line']
                users_dict[user_line] = user_dict
                del user_dict['line']
                continue
        
        return users_dict
