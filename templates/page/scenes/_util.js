// Shared helpers for the data-driven scenes. Every time comes from the voice timing (timing.js), never hard-coded seconds,
// so a re-voiced line moves its visuals with it. at('W05','double') = start of that word; throws if the word is missing.
import {w,we,ls,le,L} from '../engine.js';
export function at(line,word,k=0){return word==null?ls(line):w(line,word,k);}
export function atEnd(line,word,k=0){return word==null?le(line):we(line,word,k);}
// "*word*" -> accent span. Keeps the on-screen text short: the voice carries the sentence, the screen carries the key words.
export function accent(s,cls='b'){return String(s).replace(/\*([^*]+)\*/g,`<span class="${cls}">$1</span>`).replace(/\n/g,'<br>');}
export function hasLine(id){try{L(id);return true;}catch(e){return false;}}
