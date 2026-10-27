import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const script=fileURLToPath(new URL('../bin/devs-ai-skills.mjs',import.meta.url));
test('lists the business catalog',()=>{const p=spawnSync(process.execPath,[script,'list','--json'],{encoding:'utf8'});assert.equal(p.status,0,p.stderr);const data=JSON.parse(p.stdout);assert.ok(data.some(x=>x.name==='supplier-catalog-to-store'));});
test('returns an error for an unknown command',()=>{const p=spawnSync(process.execPath,[script,'not-a-command'],{encoding:'utf8'});assert.notEqual(p.status,0);});
