import re
from workflow import Workflow, ICON_WARNING

workflow = Workflow()
log = workflow.logger

def charsContainedInTarget(queryStr, targetStr):
    chars = list(queryStr)
    regex = '.*'.join(chars)
    regex = '.*' + regex + '.*'
    if re.match(r'%s' % regex, targetStr, re.M | re.I):
        return True
    
    return False

def strContainedInTarget(queryStr, targetStr):
    regex = '.*' + queryStr + '.*'
    if re.match(r'%s' % regex, targetStr, re.M | re.I):
        return True
    
    return False
