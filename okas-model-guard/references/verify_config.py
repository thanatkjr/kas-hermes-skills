import yaml
import os

config_path = os.path.expandvars(r'%LOCALAPPDATA%\hermes\config.yaml')
with open(config_path) as f:
    c = yaml.safe_load(f)

m = c.get('model', {})
moa = c.get('moa', {})
aux = c.get('auxiliary', {})

print('=== MAIN MODEL ===')
print(f'Provider: {m.get("provider")}')
print(f'Model:    {m.get("default")}')
print(f'Base URL: {m.get("base_url")}')
print()
print('=== MoA ===')
print(f'Enabled:  {moa.get("enabled")}')
if moa.get('enabled'):
    refs = moa.get('reference_models', [])
    agg = moa.get('aggregator', {})
    print(f'Refs:     {len(refs)} model(s)')
    for i, r in enumerate(refs):
        print(f'  [{i+1}] {r.get("provider")} · {r.get("model")}')
    print(f'Agg:      {agg.get("provider")} · {agg.get("model")}')
print()
print('=== AUXILIARY ===')
for k, v in aux.items():
    if isinstance(v, dict):
        print(f'{k}: {v.get("provider", "?")} · {v.get("model", "?")}')

# Health checks
issues = []
if m.get('provider') == 'moa':
    issues.append('❌ model.provider = moa — เปลี่ยนเป็น openrouter')
if moa.get('enabled'):
    issues.append('❌ MoA เปิดอยู่ — ปิดด้วย moa.enabled: false')
if m.get('default', '').startswith('poolside/'):
    issues.append('❌ ใช้โมเดลฟรี — เปลี่ยนเป็น deepseek/deepseek-v4-pro')

if issues:
    print('\n=== ⚠️ ISSUES ===')
    for i in issues:
        print(i)
else:
    print('\n✅ All good — no issues detected.')
