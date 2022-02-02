import io
import os
import json
import numpy as np
import logging
from PIL import Image

from fledge.common import logger
from google.cloud import pubsub_v1
from fledge.common.common import _FLEDGE_ROOT, _FLEDGE_DATA


_LOGGER = logger.setup(__name__, level=logging.INFO)

_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'Google Pub/Sub North Plugin',
         'type': 'string',
         'default': 'gcp',
         'readonly': 'true'
    },
    'projectId': {
        'description': 'GCP cloud project name',
        'type': 'string',
        'default': 'decisive-light-339213',
        'order': '1',
        'displayName': 'Project ID',
        'mandatory': 'true'
    },
    'topic': {
        'description': 'A topic forwards messages from publishers to subscribers',
        'type': 'string',
        'default': 'camera-data',
        'order': '2',
        'displayName': 'Publish Topic',
        'mandatory': 'true'
    },
    'credentials': {
        'description': 'JSON key for the service account',
        'type': 'string',
        'default': 'credentials.json',
        'order': '3',
        'displayName': 'Credentials',
        'mandatory': 'true'
    },
    'source': {
        'description': 'Source of data to be sent on the stream. May be either readings or statistics.',
        'type': 'enumeration',
        'default': 'readings',
        'options': ['readings', 'statistics'],
        'order': '4',
        'displayName': 'Source'
    }
}


def plugin_info():
    return {
        'name': 'gcp',
        'version': '1.9.2',
        'type': 'north',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(data):
    return data


def _get_certs_dir(_path):
    dir_path = _FLEDGE_DATA + _path if _FLEDGE_DATA else _FLEDGE_ROOT + '/data' + _path
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    certs_dir = os.path.expanduser(dir_path)
    return certs_dir


def _transmit_pubsub(pub, topic, data, datapoint):
    _LOGGER.info("Transmitting data to Cloud Pub/Sub...")
    _LOGGER.debug("Data type: {} & data: {}".format(type(data), data))
    if isinstance(data['readings'][datapoint], np.ndarray):
        pil_img = Image.fromarray(data['readings'][datapoint], mode='L').convert('RGB')
        img_byte_arr = io.BytesIO()
        pil_img.save(img_byte_arr, format='PNG')
        img_content = img_byte_arr.getvalue()
        _LOGGER.debug("pil image content: {}".format(img_content))
        # Add other attributes like asset, id, ts, user_ts to message
        future = pub.publish(topic, img_content, asset=data['asset'],
                             id=str(data['id']), ts=data['ts'], user_ts=data['user_ts'])
    else:
        # When you publish a message, the client returns a future.
        user_encode_data = json.dumps(data).encode('utf-8')
        _LOGGER.debug("Dict to bytes: {}".format(user_encode_data))
        future = pub.publish(topic, user_encode_data)
    _LOGGER.debug("Publish data: {}".format(data))
    _LOGGER.debug(future.result())
    _LOGGER.info("Published data to Pub/Sub topic {}".format(topic))

    # If we want to see this publish data then use subscriber client
    # Either Google console - https://console.cloud.google.com/cloudpubsub/subscription/detail
    # Or write own subscriber client - http://googleapis.dev/python/pubsub/latest/index.html#subscribing


async def plugin_send(data, payload, stream_id):
    try:
        _LOGGER.debug("data with type: {}-{}".format(type(data), data))
        _LOGGER.debug("payload with type: {}-{}".format(type(payload), payload))
        _LOGGER.debug("stream_id with type: {}-{}".format(type(stream_id), stream_id))

        # Add JSON key for service account
        # This is a prerequisite and should be placed under $FLEDGE_DATA/etc/certs/json/<.json>
        json_certs_path = "{}/{}".format(_get_certs_dir('/etc/certs/json'), data['credentials']['value'])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_certs_path

        # Publisher
        publisher = pubsub_v1.PublisherClient()
        # The `topic_path` method creates a fully qualified identifier
        # in the form `projects/{project_id}/topics/{topic_id}`
        topic_path = publisher.topic_path(data['projectId']['value'], data['topic']['value'])
        _LOGGER.debug("Publisher topic: {}".format(topic_path))
        for entry in payload:
            if 'readings' in payload[0]:
                if isinstance(entry, dict):
                    _LOGGER.debug("Entry: {}".format(entry))
                    for dp in entry['readings'].keys():
                        _LOGGER.debug("Datapoint: {}".format(dp))
                        v = entry['readings'][dp]
                        if isinstance(v, np.ndarray):
                            _LOGGER.debug("dp={}, type(v)={}, v.shape={}, v={}".format(dp, type(v), v.shape, v))
                            # This only requires when we need to send JSON asis on GCP in case of ndarray
                            # entry['readings'][dp] = v.tolist()
                        _transmit_pubsub(publisher, topic_path, entry, dp)
            else:
                _LOGGER.warning("**** 'readings' key not present in payload[0]={}".format(payload[0]))
                is_data_sent = False
                new_last_object_id = payload[-1]['id']
                num_sent = len(payload)
                _LOGGER.debug("data sent {} last object id {} num sent {}".format(is_data_sent, new_last_object_id,
                                                                                  num_sent))
                return is_data_sent, new_last_object_id, num_sent
    except Exception as ex:
        _LOGGER.exception("Data could not be sent, {}".format(str(ex)))
    else:
        is_data_sent = True
        new_last_object_id = payload[-1]['id']
        num_sent = len(payload)
        _LOGGER.debug("data sent {} last object id {} num sent {}".format(is_data_sent, new_last_object_id, num_sent))
        return is_data_sent, new_last_object_id, num_sent


def plugin_shutdown(data):
    _LOGGER.debug('{} north plugin shut down'.format(_DEFAULT_CONFIG['plugin']['default']))


def plugin_reconfigure():
    pass
