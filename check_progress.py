from pathlib import Path
import collections
files=list(Path('gcloud_cli_data').rglob('*.md'))
print('total', len(files))
depths=collections.Counter()
for f in files:
    rel=f.relative_to('gcloud_cli_data')
    depths[len(rel.parts)]+=1
print(sorted(depths.items()))
deep=[str(f) for f in files if len(f.relative_to('gcloud_cli_data').parts)>=5]
print('sample deep:', deep[:10])
# check for manifest/index
print('has manifest:', Path('gcloud_cli_data/_manifest.json').exists())
# list top dirs
top=[p for p in Path('gcloud_cli_data').iterdir() if p.is_dir()]
print('top dirs count', len(top))
print([t.name for t in top[:20]])
