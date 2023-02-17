from confluent_kafka import Producer

def read_ccloud_config(config_file):
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()
    return conf

props = read_ccloud_config("client.properties")
props["group.id"] = "python-group-1"
props["bootstrap.servers"] = 'pkc-419q3.us-east4.gcp.confluent.cloud:9092'

p = Producer(props)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

# some_data_source = ['Donghwan JJANG']

# for data in some_data_source:
#     # Trigger any available delivery report callbacks from previous produce() calls
#     p.poll(0)

#     # Asynchronously produce a message. The delivery report callback will
#     # be triggered from the call to poll() above, or flush() below, when the
#     # message has been successfully delivered or failed permanently.
#     p.produce('topic-1', data.encode('utf-8'), callback=delivery_report)

try:
    while True:
        msg = input(">> ").rstrip()
        p.poll(0)
        p.produce('topic-1', msg.encode('utf-8'), callback=delivery_report)
except KeyboardInterrupt:
    pass
finally:
    p.flush()


# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
# p.flush()