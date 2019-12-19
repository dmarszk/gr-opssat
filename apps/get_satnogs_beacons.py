#!/usr/bin/env python

import requests, datetime, time
from mx.DateTime.ISO import ParseDateTimeUTC

# CONSTANTS
BEACON_LEN = 110

def process_response(json):
    print('Fetched {} frames'.format(len(json)))
    out_frames = []
    skipped_frames = 0
    for frame in json:
        timestamp = frame['timestamp']
        observer = frame['observer']
        data_hex = frame['frame']
        data_len = len(data_hex)/2
        if data_len != BEACON_LEN:
            print('Skipping non-beacon frame from {} (len {})'.format(frame['timestamp'], data_len))
            skipped_frames += 1
            continue
        #print('{} {}'.format(frame['timestamp'], frame['frame']))
        out_frame = {
            "timestamp": ParseDateTimeUTC(timestamp),
            "observer": observer,
            "data": data_hex.decode("hex")
        }
        out_frames.append(out_frame)
    return out_frames, skipped_frames

def fetch_frames(params):
    total_frames = 0
    skipped_frames = 0
    r = requests.get("https://db.satnogs.org/api/telemetry/", params=params)
    r.raise_for_status()
    json = r.json()

    total_frames += len(json)
    out_frames, skipped_frames = process_response(json)

    while 'next' in r.links:
        next_page_url = r.links['next']['url']
        r = requests.get(url=next_page_url)
        r.raise_for_status()
        json = r.json();
        total_frames += len(json)
        new_frames, skipped_out_frames = process_response(json)
        out_frames += new_frames
        skipped_frames += skipped_out_frames

    print('Fetched {} frames in in total (Processed {}, Skipped {})'.format(total_frames, len(out_frames), skipped_frames))
    return out_frames

def main():
    duplicated = 0
    written = 0
    norad_id = 99992
    params = {'format': 'json', 'satellite': norad_id}
    frames = fetch_frames(params)
    #print frames
    lastdata = []
    f = open('opssat_frames.bin', 'wb')
    print ('Writing frames in reversed order')
    for frame in reversed(frames):
        if frame['data'] == lastdata:
            duplicated += 1
            continue
        print(frame['timestamp'].strftime('%Y/%m/%d %H:%M:%S'))
        f.write(frame['data'])
        lastdata = frame['data']
        written += 1
    f.close()
    print ('{} processed frames written to the file (removed {} duplicates)'.format(written, duplicated))

if __name__== "__main__":
    main()



