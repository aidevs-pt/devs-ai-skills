// Exercise generated browser logic with a minimal DOM. This is not a native browser test.
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';

const root=fileURLToPath(new URL('../',import.meta.url));
const skill=root+'.agents/skills/product-finder-builder/';
const run=spawnSync(process.env.DEVS_AI_PYTHON||'python',[
  skill+'scripts/build_finder.py','--input',skill+'assets/example-input.json'
],{encoding:'utf8'});
assert.equal(run.status,0,run.stderr);
const html=JSON.parse(run.stdout).html;

function page(){
  class Element{
    constructor(){this.children=[];this.value='';this.textContent='';this.handlers={};}
    append(child){this.children.push(child);}
    replaceChildren(){this.children=[];this.textContent='';}
    addEventListener(name,fn){this.handlers[name]=fn;}
    focus(){this.focused=true;}
  }
  const ids=Object.fromEntries(['finder-data','heading','quiz','results'].map(id=>[id,new Element()]));
  ids['finder-data'].textContent=html.match(/<script type="application\/json" id="finder-data">([\s\S]*?)<\/script>/)[1];
  const document={getElementById:id=>ids[id],createElement:()=>new Element()};
  const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
  vm.runInNewContext(script,{document});
  return ids;
}

test('finder initially shows only available products',()=>{
  const p=page();
  assert.deepEqual(p.results.children.map(card=>card.children[0].textContent),['Small desk lamp','Large floor lamp']);
});
test('finder selections intersect constraints and preserve no-match result',()=>{
  const p=page();
  p.quiz.children[0].children[0].value='1'; // Large room.
  p.quiz.children[1].children[0].value='0'; // Up to EUR 100.
  p.quiz.handlers.submit({preventDefault(){}});
  assert.equal(p.results.children.length,0);
  assert.match(p.results.textContent,/No matching products/);
  assert.equal(p.results.focused,true);
});
test('finder can return a matching product after changing choices',()=>{
  const p=page();
  p.quiz.children[0].children[0].value='0';
  p.quiz.children[1].children[0].value='0';
  p.quiz.handlers.submit({preventDefault(){}});
  assert.deepEqual(p.results.children.map(card=>card.children[0].textContent),['Small desk lamp']);
});
