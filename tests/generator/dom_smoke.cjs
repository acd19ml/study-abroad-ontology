/* DOM simulation only: executes the real inline UI code without a browser.
 * It checks event/data behavior, not rendering, CSS layout, or browser policies.
 * No external packages, browser automation, network, or filesystem writes.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8');
const dataMatch=html.match(/<script id="model-data" type="application\/json">([\s\S]*?)<\/script>/);
assert.ok(dataMatch,'embedded payload exists');
const templateMode=process.argv.includes('--template');
const payload=templateMode?null:JSON.parse(dataMatch[1]);
let assertions=0;
function ok(value,message){assert.ok(value,message);assertions++;}
class Element{
 constructor(tag){this.tagName=tag.toLowerCase();this.attrs={};this.children=[];this.parentElement=null;this.listeners={};this._text='';this.value='';this.checked=false;this.hidden=false;this.scrollTop=0;this.clientWidth=1024;this.clientHeight=690;this.dataset={};}
 set textContent(v){this._text=String(v);this.children=[];}
 get textContent(){return this._text+this.children.map(e=>e.textContent).join('');}
 set className(v){this.attrs.class=v;}
 get className(){return this.attrs.class||'';}
 setAttribute(k,v){this.attrs[k]=String(v);if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=String(v);}
 getAttribute(k){return this.attrs[k]??null;}
 append(...children){for(let child of children){if(typeof child!=='object'){const t=new Element('#text');t.textContent=child;child=t;}child.parentElement=this;this.children.push(child);}}
 replaceChildren(...children){this._text='';this.children=[];this.append(...children);}
 addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);}
 dispatchEvent(event){event.target??=this;event.preventDefault??=()=>{};event.stopPropagation??=()=>{};for(const fn of this.listeners[event.type]||[])fn(event);return true;}
 click(){this.dispatchEvent({type:'click'});}
 focus(){document.activeElement=this;}
 blur(){document.activeElement=null;}
 setPointerCapture(){}
 getBoundingClientRect(){return {x:0,y:0,width:this.clientWidth,height:this.clientHeight};}
 matches(selector){return selector.split(',').some(s=>{s=s.trim();const a=s.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);if(a)return a[1] in this.attrs&&(a[2]===undefined||this.attrs[a[1]]===a[2]);if(s.startsWith('.'))return this.className.split(' ').includes(s.slice(1));const parts=s.split('.');return this.tagName===parts[0]&&(!parts[1]||this.className.split(' ').includes(parts[1]));});}
 closest(selector){let e=this;while(e){if(e.matches(selector))return e;e=e.parentElement;}return null;}
 querySelectorAll(selector){const out=[];function walk(e){for(const c of e.children){if(c.matches(selector))out.push(c);walk(c);}}walk(this);return out;}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
}
const root=new Element('document'),byId=new Map();
const document={activeElement:null,createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t),
 createTextNode:t=>{const e=new Element('#text');e.textContent=t;return e;},
 getElementById:id=>byId.get(id),querySelectorAll:s=>root.querySelectorAll(s),addEventListener:()=>{}};
const markup=html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/g,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/g,'');
for(const match of markup.matchAll(/<([a-zA-Z][\w:-]*)\b([^>]*)>/g)){
 const e=new Element(match[1]);for(const a of match[2].matchAll(/([\w:-]+)(?:="([^"]*)")?/g))e.setAttribute(a[1],a[2]??'');
 if('hidden' in e.attrs)e.hidden=true;if(e.attrs.id)byId.set(e.attrs.id,e);root.append(e);
}
const data=new Element('script');data.textContent=dataMatch[1];byId.set('model-data',data);root.append(data);
const scripts=[...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)].filter(x=>!x[1].includes('application/json'));
function deepFreeze(v){if(v&&typeof v==='object'){Object.freeze(v);for(const child of Object.values(v))deepFreeze(child);}return v;}
const safeJSON={parse:s=>deepFreeze(JSON.parse(s)),stringify:JSON.stringify};
const windowEvents={};const window={addEventListener:(name,fn)=>(windowEvents[name]??=[]).push(fn)};
const context=vm.createContext({document,window,JSON:safeJSON,console,ResizeObserver:class{observe(){}},MouseEvent:class{constructor(type,opts){this.type=type;Object.assign(this,opts);}},Map,Set,Math});
for(const script of scripts)vm.runInContext(script[2],context,{timeout:5000});
if(templateMode){
 const status=document.getElementById('boot-status');
 assert.ok(status.textContent.includes('内部模板'));
 assert.ok(status.textContent.includes('generated/ps-model-explorer.html'));
 assert.equal(status.getAttribute('data-result'),'error');
 console.log('Template entry: correct-file diagnostic shown without a JSON parse crash.');
 process.exit(0);
}
const get=id=>byId.get(id),scene=get('scene'),inspector=get('inspector');
const nodes=()=>scene.querySelectorAll('[data-node-id]'),edges=()=>scene.querySelectorAll('[data-edge-id]');
const findNode=id=>nodes().find(n=>n.getAttribute('data-node-id')===id);
const findEdge=id=>edges().find(n=>n.getAttribute('data-edge-id')===id);
const change=(id,value)=>{get(id).value=value;get(id).dispatchEvent({type:'change'});};
const first=payload.elements.find(e=>e.type==='object');
ok(get('boot-status').hidden&&get('boot-status').getAttribute('data-result')==='ready','successful interactive boot is explicitly signaled');
ok(nodes().length===payload.elements.filter(e=>e.type==='object').length,'initial view includes all model objects');
ok(edges().length===payload.elements.filter(e=>e.type==='relation').length,'initial edges match explicit relations');
ok(inspector.textContent.includes(first.name),'initial selection has substantive detail');
const another=payload.elements.find(e=>e.type==='object'&&e.id!==first.id);
findNode(another.id).click();
ok(inspector.textContent.includes(another.name),'node click updates detail');
ok(another.attributes.every(a=>inspector.textContent.includes(a.meaning)),'all object attribute meanings visible');
const relation=payload.elements.find(e=>e.type==='relation');findEdge(relation.id).click();
ok(inspector.textContent.includes(relation.semantic)&&inspector.textContent.includes(relation.cardinality),'edge click exposes relation contract');
get('tab-explore').click();
const preferred=payload.elements.find(e=>e.type==='rule').applies_to[0];
ok(inspector.textContent.includes(payload.elements.find(e=>e.id===preferred).name),'command/rule view chooses a source-derived command');
const ruleNode=nodes().find(n=>n.getAttribute('data-node-id').startsWith('rule.'));
ok(Boolean(ruleNode),'applicable rules visible around command');ruleNode.click();
ok(inspector.textContent.includes('规则判断'),'rule condition visible');
get('focus').checked=false;get('focus').dispatchEvent({type:'change'});
ok(nodes().length===payload.elements.filter(e=>e.type!=='relation').length,'full model neighborhood can expand without mutating frozen source records');
get('tab-types').click();change('type-select','object');
ok(nodes().length===payload.elements.filter(e=>e.type==='object').length+1,'type view classifies actual source elements');
ok(inspector.textContent.includes('元模型类型')&&inspector.textContent.includes('aggregate'),'type properties come from schema');
get('tab-states').click();const life=payload.lifecycles[0];
ok(nodes().length===life.nodes.length,'state nodes derive from lifecycle');
ok(edges().length===life.edges.filter(e=>e.source!==e.target).length,'self-loops initially collapsed');
findEdge(life.edges.find(e=>e.source!==e.target).id).click();
ok(inspector.textContent.includes('触发命令'),'transition edge exposes source command');
get('loops').checked=true;get('loops').dispatchEvent({type:'change'});
ok(edges().length===life.edges.length,'self-loop toggle shows all source transitions');
const needle=payload.elements.find(e=>e.type==='human_decision_point').name;
get('search').value=needle;get('search').dispatchEvent({type:'input'});
ok(!get('search-results').hidden&&get('search-results').querySelector('button'),'global search finds decision points');
get('search-results').querySelector('button').click();
ok(inspector.textContent.includes(needle),'search result opens model element');
const before=get('graph').getAttribute('viewBox');get('zoom-in').click();
ok(get('graph').getAttribute('viewBox')!==before,'zoom changes camera');
const node=nodes()[0];node.dispatchEvent({type:'keydown',key:'Enter'});
ok(inspector.textContent.includes(payload.elements.find(e=>e.id===node.getAttribute('data-node-id'))?.name||''),'keyboard activates nodes');
ok(!/<script[^>]+src=|<link[^>]+href=["']https?:/i.test(html),'artifact has no network-loaded dependencies');
for(const fn of windowEvents.error||[])fn({message:'synthetic initialization failure'});
ok(!get('boot-status').hidden&&get('boot-status').textContent.includes('synthetic initialization failure'),'initialization errors are visible rather than silent blank output');
console.log(`DOM simulation: ${assertions} assertions passed; no browser rendering performed.`);
