#!/usr/bin/env node
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const script=fileURLToPath(new URL('../../scripts/devs.py',import.meta.url));
const python=process.env.DEVS_AI_PYTHON || (process.platform==='win32'?'python':'python3');
const child=spawn(python,[script,...process.argv.slice(2)],{stdio:'inherit',shell:false});
child.on('error',error=>{process.stderr.write('Cannot start Python. Set DEVS_AI_PYTHON to a Python 3.10+ executable. '+error.message+'\n');process.exitCode=2;});
child.on('exit',(code,signal)=>{process.exitCode=code ?? 2;});
