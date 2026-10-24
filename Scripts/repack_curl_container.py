"""Realign the pinned legacy universal archive; preserve every architecture payload."""
import hashlib
import json
import struct
import sys
from pathlib import Path

EXPECTED_INPUT = '20c8f6783165a8f2d2087508ea3a56b2b6c90f0eca743269c849d9e316c3b9a4'

def repack(source, destination):
    original = Path(source).read_bytes()
    assert hashlib.sha256(original).hexdigest() == EXPECTED_INPUT
    magic, count = struct.unpack_from('>II', original)
    assert magic == 0xcafebabe and count == 5
    records = []
    for index in range(count):
        cpu, subtype, offset, size, alignment = struct.unpack_from('>5I', original, 8+20*index)
        assert offset >= 8+20*count and offset+size <= len(original)
        payload = original[offset:offset+size]
        assert payload.startswith(b'!<arch>\n')
        records.append(dict(index=index, cpu=cpu, subtype=subtype, offset=offset,
                            size=size, alignment=max(alignment, 3), payload=payload))
    result = bytearray(8 + 20*count)
    struct.pack_into('>II', result, 0, magic, count)
    for record in sorted(records, key=lambda r:r['offset']):
        boundary = 1 << record['alignment']
        result.extend(b'\0' * ((-len(result)) % boundary))
        record['new_offset'] = len(result)
        result.extend(record['payload'])
        struct.pack_into('>5I', result, 8+20*record['index'], record['cpu'], record['subtype'],
                         record['new_offset'], record['size'], record['alignment'])
    checks = []
    for record in records:
        position = record['new_offset']
        preserved = bytes(result[position:position+record['size']]) == record['payload']
        assert preserved and position % 8 == 0
        checks.append({'cpu_type':record['cpu'], 'cpu_subtype':record['subtype'],
            'original_offset':record['offset'], 'new_offset':position,
            'payload_sha256':hashlib.sha256(record['payload']).hexdigest(), 'payload_preserved':preserved})
    Path(destination).write_bytes(result)
    return {'input_sha256':EXPECTED_INPUT, 'output_sha256':hashlib.sha256(result).hexdigest(),
        'all_architecture_payloads_preserved':True, 'all_payload_offsets_aligned_to_eight_bytes':True,
        'input_bytes':len(original), 'output_bytes':len(result), 'architectures':checks}

if __name__ == '__main__':
    assert len(sys.argv) == 3
    print(json.dumps(repack(sys.argv[1], sys.argv[2]), indent=2))
