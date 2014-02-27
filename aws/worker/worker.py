# Copyright 2014
# Author: Christopher Van Arsdale

import boto
from boto.sqs.message import Message
import common.base.flags as flags
import subprocess
import sys
import tempfile

FLAGS = flags.FLAGS
flags.d.DEFINE_string('input_queue', '', 'Input s3 queue.')
flags.d.DEFINE_string('output_queue', '', 'Output s3 queue.')
flags.d.DEFINE_string('error_queue', '', 'Error s3 queue.')
flags.d.DEFINE_string('execute_script', '', 'Execution script.')

# TODOS:
# 1) Visibility timeout extender background thread.
# 2) Sigterm handler
# 3) Async send/delete.

def ProcessMessage(message, input_file, output_file, script):
    input_file.write(message.get_body())
    input_file.flush()
    return subprocess.call(script, shell=True) == 0

def WriteOutput(output_f, output_queue):
    body = output_f.read()
    m = Message()
    if body is not None:
        m.set_body(body)
    else:
        m.set_body('')
    output_queue.write(m)

def WriteError(message, error_queue):
    m = Message()
    m.set_body(message.get_body())
    error_queue.write(m)

if __name__ == '__main__':
    sys.argv = FLAGS(sys.argv)  # parse flags

    # Input/output to script
    input_f = tempfile.NamedTemporaryFile()
    output_f = tempfile.NamedTemporaryFile()
    script = FLAGS.execute_script
    script = script.replace('{INPUT}', input_f.name)
    script = script.replace('{OUTPUT}', output_f.name)
 
    # SQS connection
    sqs_conn = boto.connect_sqs()
    input_queue = sqs_conn.get_queue(FLAGS.input_queue)
    if input_queue is None:
        raise 'Unknown queue: %s' % FLAGS.input_queeu

    output_queue = sqs_conn.get_queue(FLAGS.output_queue)
    if output_queue is None:
        raise 'Unknown queue: %s' % FLAGS.output_queue

    error_queue = sqs_conn.get_queue(FLAGS.error_queue)
    if error_queue is None:
        raise 'Unknown queue: %s' % FLAGS.error_queue

    while True:
        messages = input_queue.get_messages(wait_time_seconds=20,
                                            visibility_timeout=240)
        if len(messages) == 0:
            print 'No messages, retrying.'
            continue

        if ProcessMessage(messages[0], input_f, output_f, script):
            WriteOutput(output_f, output_queue)
        else:
            WriteError(messages[0], error_queue)
        input_queue.delete_message_batch(messages)
