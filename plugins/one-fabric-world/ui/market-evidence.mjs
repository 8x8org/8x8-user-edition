// Public-safe market evidence renderer shared between the user hub and Node tests.
// The importer is intentionally LOCAL_IMPORT_UNVERIFIED, never a live provider attestation.
// No credentials, account balances, orders, signing, network requests or persistence.
const MARKET_SCHEMA='8x8.public.market.snapshot.v1';
const MARKET_ALLOWED_KEYS=new Set(['schema','classification','scope','source_label','venue','instrument','interval','window_start','window_end','observed_at','market_trade_count','bars']);
const MARKET_INTERVALS=new Set(['1m','5m','15m','1h','1d']);
const MARKET_TIMESTAMP=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;
function marketTimestamp(x){return typeof x==='string'&&MARKET_TIMESTAMP.test(x)&&Number.isFinite(Date.parse(x))?Date.parse(x):NaN}
function marketDecimal(x){return typeof x==='string'&&/^\d{1,80}$/.test(x)}
function marketBad(code){return {ok:false,error:code}}
export function validateLocalMarketSnapshot(value){
 if(!value||typeof value!=='object'||Array.isArray(value))return marketBad('INVALID_OBJECT');
 if(Object.keys(value).some(k=>!MARKET_ALLOWED_KEYS.has(k)))return marketBad('UNKNOWN_OR_PRIVATE_FIELD');
 if(value.schema!==MARKET_SCHEMA||value.classification!=='LOCAL_IMPORT_UNVERIFIED'||value.scope!=='PUBLIC_MARKET_ONLY')return marketBad('NOT_A_PUBLIC_LOCAL_SNAPSHOT');
 if(typeof value.source_label!=='string'||value.source_label.length<3||value.source_label.length>80||/[^\x20-\x7E]/.test(value.source_label))return marketBad('INVALID_SOURCE_LABEL');
 if(typeof value.venue!=='string'||!/^[A-Za-z0-9._-]{2,32}$/.test(value.venue))return marketBad('INVALID_VENUE');
 if(typeof value.instrument!=='string'||!/^[A-Za-z0-9._:\/-]{2,48}$/.test(value.instrument))return marketBad('INVALID_INSTRUMENT');
 if(!MARKET_INTERVALS.has(value.interval))return marketBad('INVALID_INTERVAL');
 const start=marketTimestamp(value.window_start),end=marketTimestamp(value.window_end),observed=marketTimestamp(value.observed_at);
 if(![start,end,observed].every(Number.isFinite)||end<=start||end-start>31*86400000||observed<end)return marketBad('INVALID_TIMESTAMPS');
 if(value.market_trade_count!==null&&value.market_trade_count!==undefined&&!marketDecimal(value.market_trade_count))return marketBad('INVALID_TRADE_COUNT');
 if(!Array.isArray(value.bars)||value.bars.length<2||value.bars.length>1024)return marketBad('INVALID_BARS_LENGTH');
 const bars=[];let previous=-Infinity;
 for(const item of value.bars){
  if(!item||typeof item!=='object'||Array.isArray(item))return marketBad('INVALID_BAR');
  if(Object.keys(item).some(k=>!['timestamp','open','high','low','close','volume'].includes(k)))return marketBad('UNKNOWN_BAR_FIELD');
  const t=marketTimestamp(item.timestamp),{open,high,low,close,volume}=item;
  if(!Number.isFinite(t)||t<start||t>end||t<=previous)return marketBad('OUT_OF_ORDER_OR_OUTSIDE_WINDOW');
  if(![open,high,low,close,volume].every(x=>typeof x==='number'&&Number.isFinite(x))||low<=0||volume<0||high<Math.max(open,close)||low>Math.min(open,close)||open<=0||close<=0)return marketBad('INVALID_OHLCV');
  previous=t;bars.push({t,open,high,low,close,volume});
 }
 return {ok:true,snapshot:{
  schema:MARKET_SCHEMA,classification:'LOCAL_IMPORT_UNVERIFIED',scope:'PUBLIC_MARKET_ONLY',
  source_label:value.source_label,venue:value.venue,instrument:value.instrument,
  interval:value.interval,window_start:value.window_start,window_end:value.window_end,
  observed_at:value.observed_at,market_trade_count:value.market_trade_count??null,bars
 }};
}
export function formatMarketTradeCount(value){
 if(value===null||value===undefined)return 'UNAVAILABLE';
 if(!marketDecimal(value))return 'INVALID';
 return BigInt(value).toLocaleString('en-US');
}
export function marketClosePath(bars,width=760,height=240,pad=18){
 if(!Array.isArray(bars)||bars.length<2)return null;
 const safe=bars.every(b=>Number.isFinite(b.t)&&Number.isFinite(b.close)&&b.close>0);
 if(!safe||width<80||height<80)return null;
 const times=bars.map(b=>b.t),prices=bars.map(b=>b.close);
 const minT=Math.min(...times),maxT=Math.max(...times),lo=Math.min(...prices),hi=Math.max(...prices);
 if(maxT<=minT)return null;
 const denom=Math.max(hi-lo,Math.abs(hi)*1e-10,1e-10);
 const scaleX=t=>pad+(t-minT)/(maxT-minT)*(width-pad*2);
 const scaleY=v=>height-pad-(v-lo)/denom*(height-pad*2);
 const points=bars.map(b=>[scaleX(b.t),scaleY(b.close)]);
 const path=points.map((p,i)=>(i?'L':'M')+p[0].toFixed(2)+' '+p[1].toFixed(2)).join(' ');
 return {path,minimum:lo,maximum:hi,firstTime:minT,lastTime:maxT,firstClose:bars[0].close,lastClose:bars[bars.length-1].close,points};
}
