#!/usr/bin/env python3
"""Generate the standalone bn/cn-node Slurm dashboard (Python 3.6+, no packages)."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def command(*args):
    return subprocess.check_output(args, universal_newlines=True, stderr=subprocess.PIPE, timeout=120)


def fields(line):
    return dict(re.findall(r'(?:^|\s)(\w+)=(\S+)', line))


def read_nodes(scontrol):
    nodes = {}
    for line in command(scontrol, 'show', 'nodes', '--oneliner').splitlines():
        v = fields(line)
        name = v.get('NodeName', '')
        if re.fullmatch(r'(?:bn|cn)\d+', name):
            nodes[name] = dict(name=name, total=int(v['CPUTot']), allocated=int(v['CPUAlloc']),
                               state=v['State'], memoryTotal=int(v['RealMemory']),
                               memoryAllocated=int(v['AllocMem']), partitions=v.get('Partitions', ''), gres=v.get('Gres', ''), threadsPerCore=int(v.get('ThreadsPerCore', '1')), jobs=[])
    if not nodes:
        raise ValueError('Slurm returned no bn/cn nodes; existing output was not changed.')
    return nodes


def expand_hosts(expression):
    """Expand Slurm numeric host lists locally, avoiding one process per placement."""
    result = []
    for part in re.split(r',(?=[^\]]*(?:\[|$))', expression):
        match = re.search(r'\[([^]]+)\]', part)
        if not match:
            result.append(part)
            continue
        for entry in match.group(1).split(','):
            if '-' in entry:
                start, end = entry.split('-')
                values = [str(i).zfill(len(start)) for i in range(int(start), int(end) + 1)]
            else:
                values = [entry]
            for value in values:
                result.extend(expand_hosts(part[:match.start()] + value + part[match.end():]))
    return result


def collect(scontrol):
    nodes = read_nodes(scontrol)
    jobs = []
    host_cache = {}
    for line in command(scontrol, 'show', 'jobs', '--details', '--oneliner').splitlines():
        v = fields(line)
        if v.get('JobState') not in ('RUNNING', 'COMPLETING', 'SUSPENDED'):
            continue
        placements = []
        for hosts, cpus, mem in re.findall(r'\bNodes=(\S+) CPU_IDs=(\S+) Mem=(\d+)', line):
            if not any(prefix in hosts for prefix in ('bn', 'cn')):
                continue
            if hosts not in host_cache:
                host_cache[hosts] = expand_hosts(hosts)
            count = sum(int(part.split('-')[-1]) - int(part.split('-')[0]) + 1
                        for part in cpus.split(','))
            for host in host_cache[hosts]:
                if host in nodes:
                    nodes[host]['jobs'].append([v['JobId'], count, int(v['NumNodes']), int(mem), cpus])
                    placements.append(dict(node=host, cpus=count, memory=int(mem), ids=cpus))
        if placements:
            jobs.append(dict(id=v['JobId'], name=v.get('JobName', ''),
                             owner=v.get('UserId', '').split('(')[0], state=v['JobState'],
                             nodes=int(v['NumNodes']), cpus=int(v['NumCPUs']), partition=v.get('Partition',''), placements=placements))
    # Node and job queries are not atomic. Detect changes rather than publish inconsistent bars.
    latest = read_nodes(scontrol)
    mismatches = []
    completing = {job['id'] for job in jobs if job['state'] == 'COMPLETING'}
    for name, node in nodes.items():
        fresh = latest.get(name)
        # Slurm can retain placement details during cleanup after resources are released.
        retained = [j for j in node['jobs'] if j[0] not in completing]
        if fresh and len(retained) != len(node['jobs']) and fresh['allocated'] == sum(j[1] for j in retained) and fresh['memoryAllocated'] == sum(j[3] for j in retained):
            node['jobs'] = retained
            for job in jobs:
                if job['id'] in completing:
                    job['placements'] = [p for p in job['placements'] if p['node'] != name]
        if fresh is None or fresh['allocated'] != sum(j[1] for j in node['jobs']) or fresh['memoryAllocated'] != sum(j[3] for j in node['jobs']):
            mismatches.append(name)
        elif fresh:
            node.update({k: val for k, val in fresh.items() if k != 'jobs'})
    if set(latest) != set(nodes):
        mismatches.append('node list changed')
    jobs = [job for job in jobs if job['placements']]
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=4)))
    return dict(timestamp=stamp.isoformat(), time=stamp.strftime('%d %b %Y, %H:%M Dubai'),
                nodes=sorted(nodes.values(), key=lambda n: n['name']), jobs=jobs), mismatches


def reference_data(data):
    """Adapt the verified Slurm snapshot to the supplied dashboard's schema."""
    jobs = []
    lookup = {n['name']: n for n in data['nodes']}
    indices = {j['id']: i for i, j in enumerate(data['jobs'])}
    for index, j in enumerate(data['jobs']):
        placements = [dict(node=p['node'], cpus=p['cpus'], total=lookup[p['node']]['total'],
                           mem=p['memory'], ids=p['ids']) for p in j['placements']]
        jobs.append(dict(id=j['id'], internalId=j['id'], index=index, user=j['owner'],
                         name=j['name'], state=j['state'], nodes=j['nodes'], cpus=j['cpus'],
                         partition=j['partition'], placements=placements,
                         placementNodes=len(placements), placementCPUs=sum(p['cpus'] for p in placements)))
    nodes = []
    for n in data['nodes']:
        placements = [dict(job=indices[j[0]], cpus=j[1], mem=j[3], ids=j[4]) for j in n['jobs']]
        nodes.append(dict(name=n['name'], group=re.match(r'[a-z]+',n['name']).group(),
                          total=n['total'], allocated=n['allocated'], mem=n['memoryTotal'],
                          memAllocated=n['memoryAllocated'], state=n['state'],
                          partitions=n['partitions'], gres=n['gres'], threadsPerCore=n['threadsPerCore'],
                          jobs=placements, free=n['total']-n['allocated'],
                          memFree=n['memoryTotal']-n['memoryAllocated'],
                          blocked=bool(re.search(r'RESERV|DRAIN|DOWN|FAIL|MAINT',n['state'])),
                          partial=0<n['allocated']<n['total'],
                          single=sum(j[1] for j in n['jobs'] if j[2]==1),
                          multi=sum(j[1] for j in n['jobs'] if j[2]>1), allocationDelta=0))
    running = [j for j in jobs if j['state']=='RUNNING']
    summary = dict(running=len(running), single=sum(j['nodes']==1 for j in running),
                   multi=sum(j['nodes']>1 for j in running), configuredNodes=len(nodes),
                   totalCPUs=sum(n['total'] for n in nodes), allocatedCPUs=sum(n['allocated'] for n in nodes),
                   partialNodes=sum(n['partial'] for n in nodes), sharedNodes=sum(len(n['jobs'])>1 for n in nodes),
                   mixedTypeNodes=sum(n['single']>0 and n['multi']>0 for n in nodes),
                   idleNodes=sum(n['allocated']==0 for n in nodes), restrictedNodes=sum(n['blocked'] for n in nodes),
                   memoryBlocked=sum(n['free']>0 and n['memFree']<=0 for n in nodes), mismatches=[])
    warnings = ['Only BN and CN nodes are shown; job totals can include nodes outside this view.']
    return dict(started=data['timestamp'], ended=data['timestamp'], summary=summary,
                nodes=nodes, jobs=jobs, warnings=warnings)


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
        os.chmod(temporary, 0o644)
        os.replace(temporary, str(path))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', type=Path, default=base / 'bn-node-allocation.html')
    parser.add_argument('--template', type=Path, default=base / 'bn-dashboard-template.html')
    parser.add_argument('--scontrol', default=shutil.which('scontrol') or '/opt/slurm/default/bin/scontrol')
    parser.add_argument('--attempts', type=int, default=3, help='Snapshot consistency attempts (default: 3)')
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error('--attempts must be positive')
    try:
        template = args.template.read_text(encoding='utf-8')
        if template.count('__DATA__') != 1:
            raise ValueError('Template must contain exactly one __DATA__ placeholder.')
        if args.output.resolve() in (args.template.resolve(), Path(__file__).resolve()):
            raise ValueError('Output must not overwrite the template or generator.')
        for attempt in range(args.attempts):
            data, mismatches = collect(args.scontrol)
            if not mismatches:
                break
            print('Scheduler changed during snapshot; retrying: ' + ', '.join(mismatches), file=sys.stderr)
        else:
            raise ValueError('Could not obtain consistent node/job totals; existing output was not changed. Run again.')
        payload = json.dumps(reference_data(data), ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        atomic_write(args.output, template.replace('__DATA__', payload))
        print('{}: {} nodes, {} active jobs ({})'.format(args.output, len(data['nodes']), len(data['jobs']), data['time']))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr.strip(), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
